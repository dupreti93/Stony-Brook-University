import time
import datetime
import math
import sys
import dns.resolver
import copy
import dns.dnssec
import dns.message
import dns.rdataclass
import dns.rdatatype
import dns.query
import dns.rdtypes


class myDig:
    def __init__(self):
        self.root_servers_ip = ['198.41.0.4', '192.228.79.201', '192.33.4.12', '199.7.91.13',
                      '192.203.230.10', '192.5.5.241', '192.112.36.4', '198.97.190.53',
                      '192.36.148.17', '192.58.128.30', '193.0.14.129', '199.7.83.42',
                      '202.12.27.33']
        self.timeout = 5.0
        self.input_url=""
        self.servers_list=[]
        self.url_list=[]
        self.final_answer=[]
        self.dnssecStatus= True
        self.DNSVerification = True
        self.rrSetVerified = True
        self.DSFlag = 43
        self.kskFlag = 257
        self.algorithm = 'SHA256'
        self.record_type = ""
        self.alias_names = []
        self.alias_answer = []
        self.aliasFlag = True

    def resolve_url_as_per_record_type(self,answer,record_type):
        final_answer=[]
        for object in answer:
            if object.rdtype== record_type:
                if record_type == self.convert_to_record('A'):
                    final_answer.append(str(object.address))
                elif record_type==self.convert_to_record('NS') or record_type==self.convert_to_record('CNAME'):
                    final_answer.append(str(object.target))
                elif record_type == self.convert_to_record('MX'):
                    final_answer.append(str(object.exchange))
        return final_answer

    def convert_to_record(self,record_type):
        if record_type == 'A':
            return dns.rdatatype.A
        elif record_type == 'MX':
            return dns.rdatatype.MX
        elif record_type == 'NS':
            return dns.rdatatype.NS

    #Recursive function
    def resolve_url(self,input_url,record_type,main_server):
        try:
            input_url = dns.name.from_text(str(input_url))
            input_query = dns.message.make_query(input_url,record_type)
            output = dns.query.udp(input_query,main_server,self.timeout)
        except:
            return []

        answer_section = output.answer
        additional_section = output.additional
        authority_section = output.authority

        if len(answer_section)==0 and len(additional_section)!=0:
            #explore the additional section
            for items in additional_section:
                for server in items:
                    '''
                        DNS Section:
                            1. Chain of Trust.
                            2. Verification in the zone.
                    '''
                    isVerified = False
                    isChainOfTrustVerified = False
                    try:
                        '''
                            Querying name servers present in authority section for DS and DNSKEY records
                        '''
                        query_ds = dns.message.make_query(str(authority_section[0].name), dns.rdatatype.DS,
                                                          want_dnssec=True)
                        response_ds = dns.query.tcp(query_ds, main_server)
                        query_next = dns.message.make_query(str(authority_section[0].name), dns.rdatatype.DNSKEY,
                                                            want_dnssec=True)
                        response_next = dns.query.tcp(query_next, server.address)
                    except:
                        continue

                    if self.dnssecStatus:
                        try:
                            '''
                                Chain of Trust verification
                                	To check if the public KSK has been compromised, the DS record of parent is compared with the hash value of 
                                	the public KSK of the child zone. I have implemented this in the code where for the current server( which will 
                                	act as parent server), the public ZSK (can be identified if the flag’s value is 257) is compared with the DS 
                                	of this server and this is done recursively. So for each parent and child server pair, the DS value of the 
                                	parent(can be identified by checking if the flag is 43) will be compared with the hashed value of child’s 
                                	public KSK. I observed the hash is done using SHA256 algorithm so I have hardcoded it in class variable. 

                            '''
                            # We take a nameserver returned at this level by our function and check
                            #   Get the DS value in this server

                            response_ds_iterator = iter(response_ds.answer)
                            object = next(response_ds_iterator)
                            ds_obtained = False
                            while object and not ds_obtained:
                                for item in object.items:
                                    if item.rdtype == self.DSFlag:
                                        ds = item
                                        ds_obtained = True
                                        break
                                object = next(response_ds_iterator)

                            if ds is None:
                                return ['failed']

                            #   Get the KSK of next server
                            response_next_iterator = iter(response_next.answer)
                            object = next(response_next_iterator)
                            ds_next_obtained = False
                            while object and not ds_next_obtained:
                                for item in object.items:
                                    if item.flags == self.kskFlag:
                                        ksk_next = item
                                        ds_next_obtained = True
                                        break
                                object = next(response_next_iterator)

                            if ksk_next is None:
                                return ['failed']

                            ksk_next = dns.dnssec.make_ds(str(authority_section[0].name), ksk_next, self.algorithm)
                            if ds.digest != ksk_next.digest:
                                continue
                            isChainOfTrustVerified = True

                            '''
                                Chain of Trust Verification end.
                            '''
                        except:
                            self.dnssecStatus = False

                        if not isChainOfTrustVerified:
                            self.dnssecStatus = False

                        if len(response_next.answer) == 0:
                            continue
                    '''
                        Verification in the zone
                        For each server in the process, this is done recursively. The RRset, RRsig of RRset is fetched from the current DNS server and validated using ‘dns.dnssec.validate()’ function. 
                        This is done at each level and if an exception occurs at any level, the validation is considered to have failed. This validation is being done when we have non empty answer 
                        section to validate the whole process as final step. 
                    '''
                    if self.DNSVerification:
                        try:
                            query_rrset = dns.message.make_query(input_url, dns.rdatatype.A, want_dnssec=True)
                            response_rrset = dns.query.tcp(query_rrset,
                                                           server)  # r response will contain the RRset, RRSIG of RRset
                            if len(response_rrset.answer<2):
                                continue
                            dns.dnssec.validate(response_rrset.answer[0],response_rrset.answer[1],
                                                {dns.name.from_text(str(authority_section[0].name)):
                                                     response_rrset.answer[0]})
                            isVerified = True
                            break
                        except:
                            isVerified=False
                            self.DNSVerification = False
                            continue
                        '''
                        Verification in the zone end
                    '''
                    output = self.resolve_url(input_url,record_type,str(server.address))
                    if output:
                        return output

        if len(answer_section)==0 and len(additional_section)==0:
            #SOA record, website doesn't exist:
            if type(authority_section[0].items[0]).__name__ == "SOA":
                return ['No result']
            #Redirection so no value in answer and additional section, only authority section populated
            self.input_url = input_url
            input_url = str(authority_section[0].items[0].target)
            for server in self.root_servers_ip:
                output = self.resolve_url(input_url,self.convert_to_record("A"),server)
                if output:
                    return self.resolve_url(self.input_url,record_type,output[0][0])

        #When answer action is present:
        final_answer=[]
        for answer in answer_section:
            final_answer.append(self.resolve_url_as_per_record_type(answer,record_type))
            self.alias_names.append(self.resolve_url_as_per_record_type(answer, self.convert_to_record("CNAME")))
            '''
                VERIFYING THE RRSET IF WE HAVE RESPONSE IN ANSWER SECTION
            '''
            try:
                query_rrset = dns.message.make_query(input_url, dns.rdatatype.A, want_dnssec=True)
                response_rrset = dns.query.tcp(query_rrset, server)  # r response will contain the RRset, RRSIG of RRset
                if len(response_rrset.answer)<2:
                    continue
                dns.dnssec.validate(response_rrset.answer[0], response_rrset.answer[1], {dns.name.from_text(str(input_url)): response_rrset.answer[0]})
            except:
                self.rrSetVerified=False
            '''
                VERIFICATION OF RRSET COMPLETE
            '''
        return final_answer



def mydig(arguments):
    '''
        INPUT SECTION
    '''
    obj = myDig()
    '''
        GET THE DOMAIN
    '''
    obj.input_url = str(arguments[0])
    '''
        GET THE TYPE OF DNS REDOLUTION
    '''
    obj.record_type = str(arguments[1])
    record_type = obj.convert_to_record(obj.record_type)

    '''
        CALLING RESOLUTION METHOD
    '''
    root_server_iterator = iter(obj.root_servers_ip)
    root_server = next(root_server_iterator)

    start_time = time.time()

    while(len(obj.final_answer)==0):
        obj.final_answer = obj.resolve_url(obj.input_url,record_type,root_server)
        root_server = next(root_server_iterator)

    if len(obj.alias_names)>0:
        root_server_iterator = iter(obj.root_servers_ip)
        root_server = next(root_server_iterator)
        for object in obj.alias_names:
            temp_alias_answer=[]
            while (len(temp_alias_answer) == 0 and len(object)>0):
                temp_alias_answer = obj.resolve_url(str(object[0]), record_type, root_server)
                obj.alias_answer.append(temp_alias_answer)
                root_server = next(root_server_iterator)

    rumtime = time.time()-start_time

    if not obj.dnssecStatus or not obj.rrSetVerified:
        print("DNSSEC verification failed")
    elif not obj.DNSVerification:
        print("DNSSEC not supported")
    else:
        if type(obj.input_url).__name__ == "Name":
            obj.input_url = obj.input_url.to_text()
        '''
            OUTPUT SECTION
        '''
        formattedOutput = ""
        formattedOutput += "QUESTION SECTION:\n"
        formattedOutput += obj.input_url + " IN " + obj.record_type + "\n\n"
        formattedOutput += "ANSWER SECTION:\n"
        # Answer section
        for object in obj.final_answer:
            for item in object:
                if len(item) > 0:
                    formattedOutput += obj.input_url + " IN " + obj.record_type + " " + obj.formatString(str(item)) + "\n"
        # Fetching addresses for alias/canonical names
        for object in obj.alias_answer:
            if len(object) > 0:
                for item in object:
                    if len(item) > 0:
                        formattedOutput += obj.input_url + " " + " IN " + obj.formatString(str(item)) + "\n"
        formattedOutput += "\n" + "Query Time: " + str(rumtime) + " sec\n"
        formattedOutput += "WHEN: " + datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y\n")
        formattedOutput += "MSG SIZE rcvd: " + str(sys.getsizeof(obj.final_answer))

        print(formattedOutput)

if __name__ == "__main__":
    mydig(sys.argv[1:])
