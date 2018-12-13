#define NetPlace(d) chan d = [18] of {byte, byte}

/*###############################################*/

chan cha =[18] of {byte,byte}; hidden byte j, size_cha;
	NetPlace(SN1);
	NetPlace(SN2);
	byte SN3 = 0;

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

/*###############################################*/

#define sp(a,b)	set_priority(a,b)

/*###############################################*/

chan gbChan = [18] of {byte, byte, byte, chan};

/*###############################################*/ 

proctype ENA (chan pc){
	byte p1 = 1; byte p2;

	endl: do
		:: atomic {empty(gbChan) && p1 > 0 && !pc ?? [eval(_pid),1] -> 

		pc !! _pid, 1;
		printf("Transição ENA em espera \n\n");

		}
		
		:: atomic {gbChan ? _,eval(_pid),1,pc -> 

		p1--;p2++;
		printf("Transição ENA disparada \n\n");

		}
		od
}

/*###############################################*/

proctype ENB (chan pc){
	byte p3 = 1; byte p4;

	endl: do
		:: atomic {empty(gbChan) && p3 > 0 && !pc ?? [eval(_pid),2] -> 

		pc !! _pid, 2;
		printf("Transição ENB em espera \n\n");


		}
		:: atomic {gbChan ? _,eval(_pid),2,pc -> 

		p3--;p4++;
		printf("Transição ENB disparada \n\n");

		}
		od
}

/*###############################################*/

byte SN0 = 1;

init {
	

	atomic{
		printf("SN setting initial marking");

	}

	end0: do
		:: atomic{ empty(gbChan) && SN0 > 0 -> 
			sp(_pid, 6);
			SN0--;
			nt = run ENA(SN1); SN1 !! nt, 15;
			nt1 = run ENB(SN1); SN1 !! nt1, 15;
			sp(_pid,1);
			printf("Produzindo net tokens \n\n");
		}
		:: atomic{ empty(gbChan) && SN1 ?? [_,1] -> 
			sp(_pid, 6);

			recMsg(SN1, nt, 1);
			transpNetTok(SN1,SN2,nt);
			SN3++;
			gbChan !! 6-5, nt,1,SN2;
			sp(nt, 5);
			sp(_pid, 1);
			printf("SM2 Recebendo A \n\n");
			printf("SN3 %d\n", SN3);
		}

		:: atomic{empty(gbChan) && SN1 ?? [_,2] -> 
			sp(_pid, 6);

			recMsg(SN1, nt1, 2);
			transpNetTok(SN1,SN2,nt1);
			gbChan !! 6-5, nt1,2,SN2;
			sp(nt1, 5);
			sp(_pid, 1);
			printf("SN2 Recebendo B \n\n");
		}
	od
}