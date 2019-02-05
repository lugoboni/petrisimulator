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
byte S4 = 0;
byte S5 = 4;
byte S1 = 1;
NetPlace(S2);
NetPlace(S3);
NetPlace(S6);
init {

   atomic{
       printf("SN setting initial marking\n\n");
   }

   endl: do
       ::atomic{ empty(gbChan) && S3 ?? [_,1]  && S1 > 0 ->
           sp(_pid,6);
           recMsg(S3, nt, 1);
           transpNetTok(S3,S6,nt);
           gbChan !! 6-5, nt,1,S6;
           sp(nt, 5);
           printf("S6 Recebendo x \n\n");
           S1 = S1 + 1;
           S1 = S1 - 1;
           sp(_pid,1);
       }

       ::atomic{ empty(gbChan) && S2 ?? [_,2]  && S5 > 1 ->
           sp(_pid,6);
           recMsg(S2, nt, 2);
           transpNetTok(S2,S3,nt);
           gbChan !! 6-5, nt,1,S3;
           sp(nt, 5);
           printf("S3 Recebendo x \n\n");
           S4 = S4 + 1;
           S5 = S5 - 1;
           sp(_pid,1);
       }

       ::atomic{ empty(gbChan) && S1 > 0 ->
           sp(_pid,6);
           nt = run ENr(S2); S2 !! nt, 15;
           printf("Produzindo net tokens \n\n");
           S1 = S1 + 1;
           S1 = S1 - 1;
           sp(_pid,1);
       }

       ::atomic{ empty(gbChan) && S6 ?? [_,3]  && S4 > 1 ->
           sp(_pid,6);
           S5 = S5 + 1;
           S4 = S4 - 1;
           consNetTok(S6, 3);
           printf(" Consuming x from S6 \n\n");
           sp(_pid,1);
       }

       ::atomic{ empty(gbChan) && S2 ?? [_,4]  && S4 > 1 ->
           sp(_pid,6);
           S4 = S4 + 1;
           S4 = S4 - 1;
           consNetTok(S2, 4);
           printf(" Consuming x from S2 \n\n");
           sp(_pid,1);
       }

   od
}
proctype ENENWorker (chan pc){
   byte W2 = 1;
   byte W0 = 0;
   byte W1 = 0;
   byte W3 = 0;
   byte W4 = 0;
   byte T = 0;
   endl: do
       ::atomic {gbChan ? _,eval(_pid),4,pc ->
           printf("Transicao netId15486760430633 disparada\n\n");

           W1 = W1 + 1;
           W2 = W2 - 1;
       }

       ::atomic {empty(gbChan) && !pc ?? [eval(_pid),4] && W2 > 0 ->
           pc !! _pid, 4;

           printf("Transicao netId15486760430633 em espera\n\n");

       }

       ::atomic {gbChan ? _,eval(_pid),2,pc ->
           printf("Transicao netId15486760430635 disparada\n\n");

           W3 = W3 + 1;
           W2 = W2 - 1;
       }

       ::atomic {empty(gbChan) && !pc ?? [eval(_pid),2] && W2 > 0 ->
           pc !! _pid, 2;

           printf("Transicao netId15486760430635 em espera\n\n");

       }

       ::atomic {gbChan ? _,eval(_pid),3,pc ->
           printf("Transicao netId154867604306325 disparada\n\n");

           W0 = W0 + 1;
           W4 = W4 - 1;
       }

       ::atomic {empty(gbChan) && !pc ?? [eval(_pid),3] && W4 > 0 ->
           pc !! _pid, 3;

           printf("Transicao netId154867604306325 em espera\n\n");

       }

       ::atomic {empty(gbChan) && 1 ->
           T = T + 1;
       }

       ::atomic {gbChan ? _,eval(_pid),1,pc ->
           printf("Transicao netId154867604306321 disparada\n\n");

           W4 = W4 + 1;
           W3 = W3 - 1;
       }

       ::atomic {empty(gbChan) && !pc ?? [eval(_pid),1] && W3 > 0 ->
           pc !! _pid, 1;

           printf("Transicao netId154867604306321 em espera\n\n");

       }

       ::atomic {empty(gbChan) && W1 > 0 ->
           W2 = W2 + 1;
           W1 = W1 - 1;
       }

       ::atomic {empty(gbChan) && W0 > 0 && T > 0 ->
           W1 = W1 + 1;
           W0 = W0 - 1;
           T = T - 1;
       }

   od
}

/*###############################################*/

