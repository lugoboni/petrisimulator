#define NetPlace(d) chan d = [18] of {byte, byte}


/*###############################################*/


chan cha =[18] of {byte,byte}; hidden byte j, size_cha;


/*###############################################*/


inline consNetTok(c, p) {
  do:: c ?? [eval(p),_] -> c ?? eval(p),_;
    :: else -> break
  od; skip }


inline rmConf(l){
  if :: pc ?? [eval(_pid),l] -> pc ?? eval(_pid),l
     :: else fi
}


/*###############################################*/


inline transpNetTok(ch, och, p){
  do:: ch ?? [eval(p),_] ->
       ch ?? eval(p),lt;
       och !! p,lt;
    :: else -> break
  od; skip }


/*###############################################*/
hidden byte i;
hidden unsigned nt:4,lt:4, nt1:4, lt1:4;


inline recMsg(ch,f0,f1) {             /* ch - ordered "channel, f0 - output variable, f1 - constant value */
ch ! 0,f1;
do :: ch ?? f0,f1;
       if :: f0>0 ->   ch !  f0,f1; 
                       cha ! len(cha)+1,f0;
          :: else -> break
       fi
od;


 /* select ( j : 1 .. size_cha); */


    size_cha= len(cha);
   j = 1;
   do
   :: j < size_cha -> j++
   :: break
   od


cha ?? <eval(j),f0>;


 /* restoring the ordering of the input channel */
  
do :: len(cha)>0 -> 
   cha?_,nt1;
   ch ?? eval(nt1),eval(f1);
   ch !! nt1,f1;
   :: else -> break
od; 


ch ?? eval(f0),f1;   /* message selected by the receive */


}


/*###############################################*/


#define sp(a,b)    set_priority(a,b)


/*###############################################*/


chan gbChan = [18] of {byte, byte, byte, chan};


/*###############################################*/ 
NetPlace(account);
byte deposited = 0;
byte created = 0;
byte init = 1;
byte amount = 0;
init {

   atomic{
       printf("SN setting initial marking\n\n");
   }

   endl: do
       ::atomic{ init > 0 &&  ->
           sp(_pid,6);
           nt = run ENN(created); created !! nt, 15;
           printf("Produzindo net tokens \n\n");
           init--;
           created++;
           nt = run ENN(account); account !! nt, 15;
           printf("Produzindo net tokens \n\n");
           init--;
           sp(_pid,1);
       }

       ::atomic{ deposited > 0 &&  ->
           sp(_pid,6);
           deposited--;
           amount++;
           deposited--;
           sp(_pid,1);
       }

       ::atomic{ created > 0 &&  ->
           sp(_pid,6);
           created--;
           deposited++;
           created--;
           sp(_pid,1);
       }

   od
}
