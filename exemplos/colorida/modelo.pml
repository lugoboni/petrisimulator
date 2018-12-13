#define NetPlace(d) chan d = [18] of {byte, byte}

/* typedef NetPlace { chan d = [18] of {byte, byte} }
    {_pid, lab} 
   the identity field was removed since labels have a 
   single occurrence in each element net. 
 */



hidden byte i;
hidden unsigned nt:4,lt:4, nt1:4, lt1:4; 


c_code{

  typedef struct QNP {
      uchar Qlen; /* q_size */
      uchar _t;   /* q_type */
      struct {
          uchar fld0, fld1;
      } contents[18];
  } QNP;

  int numMsg(uchar *z, int lab){
      int n = ((Q0 *)z)->Qlen;
      int c = 0, k = 0;
      for (; k<n; k++)
        if ( ((QNP *)z)->contents[k].fld1 == lab )   c++;
      return c; }
};


inline consNetTok(c, p) {
  do:: c ?? [eval(p),_] -> c ?? eval(p),_;
    :: else -> break
  od; skip }

inline rmConf(l){
  if :: pc ?? [eval(_pid),l] -> pc ?? eval(_pid),l
     :: else fi
}

inline transpNetTok(ch, och, p){
  do:: ch ?? [eval(p),_] ->
       ch ?? eval(p),lt;
       och !! p,lt;
    :: else -> break
  od; skip }
  



/* deterministic receive */

inline recMsg1(ch,f0,f1) { ch ?? f0,f1; } 


/* non-deterministic receive */

chan cha =[18] of {byte,byte}; hidden byte j, size_cha;


inline recMsg(ch,f0,f1) {             /* ch - ordered channel, f0 - output variable, f1 - constant value */
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
  
do :: len(cha)>0 -> cha?_,nt1; ch ?? eval(nt1),eval(f1); ch !! nt1,f1;
   :: else -> break
od; 

ch ?? eval(f0),f1;   /* message selected by the receive */

}


#define sp(a,b)	set_priority(a,b)

/* Integer representation of labels
  -i = 1,  -r  = 3,  -lf  = 4,   c  = 5, 
  -0 = 10 (not 255!)   */


chan gbChan = [18] of {byte, byte, byte, chan}; 

/* {priority, _pid, lab, chan} 
   the bit field was removed since each element net 
   can be either removed or transported but not both
 */

unsigned Tasks:2 = 2 ; byte Results;

NetPlace(Agents); NetPlace(L1); NetPlace(L2); NetPlace(L3); NetPlace(L4); NetPlace(Lf); 


proctype agentNet(chan pc; bit na,nc; byte nr){ 
bit p1=1; unsigned p2a:2, p2r:2, p2c:2;  bit p3; 
end0:do  :: atomic{ empty(gbChan) &&  p1>0 && p2a>0 ->                              /* u2 */ 
                     sp(_pid, 6);
                     p1--; p2a--; rmConf(5); rmConf(3); p3++;
                     sp(_pid, 1) } 
         :: atomic{ empty(gbChan) &&  p3>0 ->                                       /* last */ 
                     sp(_pid, 6);
                     p3--; p1++; Results++;
                     sp(_pid, 1) } 
         :: atomic{ empty(gbChan) &&  ! pc??[eval(_pid),1] -> pc!!_pid,1 }          /* rq -i */
         :: atomic{ empty(gbChan) &&  p1>0 && p2r>0 &&
                                      ! pc??[eval(_pid),3] -> pc!!_pid,3 }          /* rq -r */
         :: atomic{ empty(gbChan) &&  p1>0 && p2c>0 && 
                                      ! pc??[eval(_pid),5] -> pc!!_pid,5 }           /* rq c */
         :: atomic{ empty(gbChan) &&  pc??[eval(_pid),5]  &&  
                          c_expr{ numMsg(qptr(PagentNet->pc-1), 5)>=3 } -> 
                     sp(_pid, 6);
  
                     pc??eval(_pid),5;             /* hor sync for label c */
                     
                     recMsg(pc, nt,5); 
                     gbChan !! 6-4,nt,5,pc; sp(nt, 4);
                     
                     recMsg(pc, nt,5); 
                     gbChan !! 6-4,nt,5,pc; sp(nt, 4);
                     
                     gbChan !! 6-4,_pid,5,pc; sp(_pid, 4); } 
         :: atomic{ gbChan ? _,eval(_pid),lt,pc -> 
                        if   :: lt==1 ->                                        /* -i */
                                p2a = p2a+na; p2r = p2r+nr; p2c = p2c+nc;
                             :: lt==3 && p1>0 && p2r>0 ->					    /* -r */ 
                                p1--; p2r--; rmConf(5); p3++ 
                             :: lt==5 && p1>0 && p2c>0 ->						/* c */ 
                                p1--; p2c--; rmConf(3); p3++ 
                             :: lt==10 -> skip 
                         fi; 
                         sp(_pid, 1) 
                   }

      od }
/*----------- end proctype -----------*/
                                    

proctype P1(){
chan pc; NetPlace(pA); NetPlace(pR); bit p4=1, p8, p5,p6,p7;
atomic{ gbChan ? _,eval(_pid),10,pc; sp(_pid,1); }
do
::  atomic{ empty(gbChan) &&  p4>0 && Results >= 5 ->
            sp(_pid, 6);
            p4--; p8++;                              /* unlab (left-down) */
            sp(_pid, 1) }
:: atomic{ empty(gbChan) &&  p4>0 && Tasks>0 &&
                 c_expr { numMsg(qptr(now.Agents-1),10)>=3 } ->
           sp(_pid, 6);
           p4--; Tasks--; p5++;                        /* unlab (left-up) */
           
           /* transport x without sync */
           recMsg(Agents, nt,10); transpNetTok(Agents,pA,nt); pA !! nt,10;
           gbChan !! 6-3, nt,10,pA; sp(nt, 3);
           
           /* transport y without sync */
           recMsg(Agents, nt,10); transpNetTok(Agents,pA,nt);pA !! nt,10;
           gbChan !! 6-3, nt,10,pA; sp(nt, 3);
           
           /* transport z without sync */
           recMsg(Agents, nt,10); transpNetTok(Agents,pA,nt); pA !! nt,10;
           gbChan !! 6-3, nt,10,pA; sp(nt, 3);
           
           sp(_pid, 1) }
:: atomic{ empty(gbChan) &&  p5>0 && c_expr { numMsg(qptr(PP1->pA-1),1)>=3 } ->
           sp(_pid, 6);                                     /* i */
           p5--; p6++;
           /* transport x - sync & move to the same place */
           recMsg(pA, nt,1); gbChan !! 6-5, nt,1,pA; sp(nt, 5);
           
           /* transport y - sync & move to the same place */
           recMsg(pA, nt,1); gbChan !! 6-5, nt,1,pA; sp(nt, 5);
           
           /* transport z - sync & move to the same place */
           recMsg(pA, nt,1); gbChan !! 6-5, nt,1,pA; sp(nt, 5);
           
           sp(_pid, 1) }
:: atomic{ empty(gbChan) &&  p6>0 && c_expr { numMsg(qptr(PP1->pA-1),3)>=3 } ->
           sp(_pid, 6);                                     /* r */
           p6--; p7++;
           recMsg(pA, nt,3); transpNetTok(pA,L1,nt);        /* transport x */
           gbChan !! 6-5, nt,3,L1; sp(nt, 5);
           
           recMsg(pA, nt,3); transpNetTok(pA,L2,nt);        /* transport y */
           gbChan !! 6-5, nt,3,L2; sp(nt, 5);
           
           recMsg(pA, nt,3); transpNetTok(pA,L3,nt);        /* transport z */
           gbChan !! 6-5, nt,3,L3; sp(nt, 5);
           
           sp(_pid, 1) }
:: atomic{ empty(gbChan) &&  p7>0 ->                      /* unlab (right) */
           sp(_pid,6);
           p7--;
           nt = run P1(); pR !! nt,10;
           gbChan !! 6-2,nt,10,pR; sp(nt, 2); }
:: atomic{ empty(gbChan) &&  pR ?? [_,4] ->                         /* lf */
           sp(_pid, 6);
           
           /* consume */
           recMsg(pR, nt,4); consNetTok(pR,nt);
           gbChan !! 6-5,nt,4,pR; sp(nt, 5);
           p8++;
           
           sp(_pid, 1) }
:: atomic{ empty(gbChan) &&  p8>0 && 
                         ! pc ?? [eval(_pid),4] -> pc !! _pid,4; }
:: atomic{ gbChan ? _,eval(_pid),lt,pc ->
           if  :: lt==4 ->  p8--; break                           /* -lf */
               :: lt==10 -> skip      /* This option can be removed since  */
           fi;                        /* the net is never transported      */
           sp(_pid,1) }
od }
/*----------- end proctype -----------*/



NetPlace(L5); bit pOut;

ltl p {<>[]( Tasks==0 &&  pOut==1 && len(Agents)==3 &&
             len(L1)==0 && len(L2)==0 && len(L3)==0 &&
             len(L4)==0 && len(L5)==0 && len(Lf)==0 ) }


/* equivalent property */
ltl p1 {<>[]( Tasks==0 &&  pOut==1 && len(Agents)==3 &&
             Agents??[1,10] && Agents??[2,10] && Agents??[3,10]  ) }


init{ NetPlace(pw1); bit pIn=1;
atomic{ /* Initial Marking */ 
  sp(_pid,2)
  nt = run agentNet(Agents, 0, 1, 3); Agents !! nt,10; 
  nt = run agentNet(Agents, 0, 1, 3); Agents !! nt,10; 
  nt = run agentNet(Agents, 0, 1, 3); Agents !! nt,10; 
  sp(_pid,1)
} 
end0: do /*************** Environment ***************/
        :: atomic{ empty(gbChan) &&  L1 ?? [_,3] ->               /* r (left-up) */
                    sp(_pid, 6);
                            
                    recMsg(L1, nt,3);				        /* transport x */ 
                    transpNetTok(L1,L4,nt); 
                    gbChan !! 6-5, nt,3,L4;
                    sp(nt, 5); 
                    
                    sp(_pid, 1) } 
        :: atomic{ empty(gbChan) &&  L2 ?? [_,3] && L3 ?? [_,3] ->    /* r (left-down) */
                    sp(_pid, 6);
                            
                    recMsg(L2, nt,3);						/* transport y */ 
                    transpNetTok(L2,L5,nt); 
                    gbChan !! 6-5, nt,3,L5; 
                    sp(nt, 5); 
                    
                    recMsg(L3, nt,3);						/* transport z */ 
                    transpNetTok(L3,L4,nt); 
                    gbChan !! 6-5, nt,3,L4;
                    sp(nt, 5); 
                    
                    sp(_pid, 1) } 
        :: atomic{ empty(gbChan) &&  L4 ?? [_,3] && L5 ?? [_,3] ->          /* r (right) */ 
                    sp(_pid, 6);
                            
                    recMsg(L4, nt,3);						/* transport x */ 
                    transpNetTok(L4,Lf,nt); 
                    gbChan !! 6-5,nt,3,Lf; 
                    sp(nt, 5); 
                    
                    recMsg(L5, nt,3);						/* transport y */ 
                    transpNetTok(L5,Lf,nt); 
                    gbChan !! 6-5,nt,3,Lf;
                    sp(nt, 5); 
                    
                    sp(_pid, 1) } 
        :: atomic{ empty(gbChan) &&  Lf ?? [_,10] ->      /* unlab (left) */
                    sp(_pid, 6);
                            
                    recMsg(Lf, nt,10);                    /* transport x */ 
                    transpNetTok(Lf,Agents,nt); 
                    Agents !! nt,10; 
                    gbChan !! 6-3,nt,10,Agents;
                    sp(nt, 3); 
                    
                    sp(_pid, 1) } 
                    
        /*************** Protocol Call ***************/
        :: atomic{ empty(gbChan) &&  pIn>0 ->             /* unlab (right) */
                    sp(_pid, 6);
                            
                    pIn--;
                    nt = run P1() priority 2; pw1 !! nt,10; 
                    gbChan !! 6-2,nt,10,pw1; sp(nt, 2); 
                    
                    sp(_pid, 1) } 
        :: atomic{ empty(gbChan) &&  pw1 ?? [_,4] ->     /* lf */
        
                    sp(_pid, 6);
                            
                    recMsg(pw1, nt,4);					 /* consume */ 
                    consNetTok(pw1,nt); 
                    gbChan !! 6-5,nt,4,pw1; 
                    sp(nt, 5); 

                    pOut++;
                    
                    sp(_pid, 1) } 
od }
