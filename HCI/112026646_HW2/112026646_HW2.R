#Statistical significant testing for dataset-1

content = read.csv(file.choose(),header = T,sep = ",")
#Please choose the file dataset 18_1.csv provided in the same directory as code when the first selection pop up opens.

attach( content )
names(content)

#Conducting pairwise T test
pairwise.t.test( time,menu,p.adjust.method ="bonferroni" )

tp = subset(content, menu=="toolpalette" )
cm = subset(content, menu=="controlmenu" )
tg = subset(content,menu=="toolglass")
fd = subset(content, menu=="flowmenu" )


#Boxplot graph
boxplot( tg[,2],fd[,2],tp[,2],cm[,2],names=c("toolglass","flowmenu","toolpalette","controlmenu"),xlab ="Menu", ylab = "Time", main = "Boxplot(Time vs Menu) : DataSet-1" )

#Conducting anova
anovaForDataset1 = aov( time ~ menu )
summary( anovaForDataset1 )



#Statistical significant testing for dataset-2 
content2 = read.csv(file.choose(),header = T,sep = ",")
#Please choose the file dataset 18_2.csv provided in the same directory as code when the second selection pop up opens.

names(content2)
attach(content2)

#Conducting pairwise T test
pairwise.t.test( time,menu, paired = TRUE,p.adjust.method = "bonferroni" )
pairwise.t.test( error,menu, paired = TRUE, p.adjust.method = "bonferroni" )

tp = subset(content2,menu == "toolpalette" )
cm = subset(content2,menu == "controlmenu" )
tg = subset(content2,menu=="toolglass")
fd = subset(content2,menu == "flowmenu" )


#Boxplot graph
boxplot(tg[,2],fd[,2],tp[,2],cm[,2],names=c("toolglass","flowmenu","toolpalette","controlmenu"),xlab ="Menu", ylab = "Time", main = "Boxplot (Time vs Menu): DataSet-2" )
boxplot(tg[,3],fd[,3],tp[,3],cm[,3],names=c("toolglass","flowmenu","toolpalette","controlmenu"),xlab ="Menu", ylab = "Error", main = "Boxplot (Error vs Menu): DataSet-2" )

#Conducting manova
manovaForDataset2 = manova(cbind(time,error)~menu+Error(user/menu),content2)
summary (manovaForDataset2,tol=0)
