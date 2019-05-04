import time
import datetime
import sys
import dns.rdatatype
import dns.query


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
        self.record_type=""
        self.alias_names=[]
        self.alias_answer=[]
        self.aliasFlag=True

    '''
        FILTERING THE ANSWER SECTION BASED ON REQUIRED DNS RESOLUTION TYPE
    '''
    def resolve_url_as_per_record_type(self,answer,record_type):
        final_answer=[]
        for object in answer:
            if object.rdtype== record_type:
                if record_type == self.convert_to_record('A'):
                    final_answer.append(str(object.address))
                elif record_type==self.convert_to_record('NS'):
                    final_answer.append(str(object.target))
                elif record_type==self.convert_to_record('CNAME'):
                    final_answer.append(str(object.target))
                elif record_type == self.convert_to_record('MX'):
                    final_answer.append(str(object.exchange))
        return final_answer

    '''
        FOR REMOVAL OF SQUARE BRACKETS AND QUOTES
    '''
    def formatString(self,s):
        new_s=""
        for i in range(len(s)):
            if s[i]=='[' or s[i]==']' or s[i]=='\'':
                continue
            new_s+=s[i]
        return new_s

    '''
        GETTING THE DATATYPE NUMERICAL VALUE FOR A STRING DNS RESOLUTION TYPE SO THAT IT WORKS WITH DNSPYTHON LIBRARY
    '''
    def convert_to_record(self,record_type):
        if record_type == 'A':
            return dns.rdatatype.A
        elif record_type == 'MX':
            return dns.rdatatype.MX
        elif record_type =='CNAME':
            return dns.rdatatype.CNAME
        elif record_type == 'NS':
            return dns.rdatatype.NS

    '''
        RECURSIVE DNS RESOLUTION FUNCTION
    '''
    def resolve_url(self,input_url,record_type,server):
        try:
            input_url = dns.name.from_text(str(input_url))
            input_query = dns.message.make_query(input_url,record_type)
            output = dns.query.udp(input_query,server,self.timeout)
        except:
            return []

        answer_section = output.answer
        additional_section = output.additional
        authority_section = output.authority

        '''
            WHEN ANSWER SECTION IS EMPTY, THE NEXT LEVEL SERVERS ARE PRESENT IN ADDITIONAL SECTION
        '''
        if len(answer_section)==0 and len(additional_section)!=0:
            #explore the additional section
            for items in additional_section:
                for server in items:
                    output = self.resolve_url(input_url,record_type,str(server.address))
                    if output:
                        return output

        if len(answer_section)==0 and len(additional_section)==0:
            '''
                SOA RECORD IN AUTHORITY SECTION WHICH TELLS US THAT DOMAIN DOESN'T EXIST.
            '''
            if type(authority_section[0].items[0]).__name__ == "SOA":
                return ['No result']
            '''
                REDIRECTION SECTION - NO VALUE IN ANSWER AND ADDITIONAL SECTION, ONLY AUTHORITY SECTION POPULATED, SO QUERYING 
                THIS DATA FOR IP WITH DOMAIN NAME FROM THIS DATA AND ROOT SERVERS AS STARTING POINT.
            '''
            self.input_url = input_url
            input_url = str(authority_section[0].items[0].target)
            for server in self.root_servers_ip:
                output = self.resolve_url(input_url,self.convert_to_record("A"),server)
                if output:
                    return self.resolve_url(self.input_url,record_type,output[0][0])
            '''
                REDIRECTION SECTION ENDS
            '''

        '''
                WHEN ANSWER SECTION IS PRESENT, WE POPULATE THE FINAL_ANSWER LIST WITH THE OBTAINED RESULTS
        '''
        final_answer=[]
        '''
                IT MAY HAPPEN THAT ANSWER SECTIONS CONTAIN CNAMES, SO WE NEED TO QUERY FOR SUCH RECORDS AGAIN STARTING FROM ROOT 
                SERVERS SO WE SAVE THESE RESULTS IN ALIAS_NAME LIST FOR FUTURE.
        '''
        alias_names=[]
        for answer in answer_section:
            final_answer.append(self.resolve_url_as_per_record_type(answer,record_type))
            self.alias_names.append(self.resolve_url_as_per_record_type(answer,self.convert_to_record("CNAME")))

        return final_answer


def mydig(arguments):
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
    '''
    '''
    while(len(obj.final_answer)==0):
        obj.final_answer = obj.resolve_url(obj.input_url,record_type,root_server)
        root_server = next(root_server_iterator)
    '''
        IF CNAME LIST alias_list IS EMPTY, THEN WE RESOLVE THESE DOMAINS AS WELL TO GET FINAL IP ADDRESSES.
    '''
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

    '''
        OUTPUT SECTION
    '''
    if type(obj.input_url).__name__=="Name":
        obj.input_url=obj.input_url.to_text()
    formattedOutput = ""
    formattedOutput += "QUESTION SECTION:\n"
    formattedOutput += obj.input_url + " IN " + obj.record_type + "\n\n"
    formattedOutput += "ANSWER SECTION:\n"
    #Answer section
    for object in obj.final_answer:
            for item in object:
                if len(item) > 0:
                    formattedOutput += obj.input_url + " IN " + obj.record_type + " " +obj.formatString(str(item))+"\n"
    # Fetching addresses for alias/canonical names
    for object in obj.alias_answer:
        if len(object)>0:
            for item in object:
                if len(item)>0:
                    formattedOutput += obj.input_url + " " + " IN "+obj.formatString(str(item))+"\n"
    formattedOutput += "\n" + "Query Time: " + str(rumtime) + " sec\n"
    formattedOutput += "WHEN: "+datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y\n")
    formattedOutput += "MSG SIZE rcvd: " + str(sys.getsizeof(obj.final_answer))

    print(formattedOutput)


if __name__ == "__main__":
    mydig(sys.argv[1:])
