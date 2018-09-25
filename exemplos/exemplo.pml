init{

byte p1 = 1, p2 = 1, p3 = 0, p4 = 0, p5 = 0;

do :: atomic{p1 >= 1 -> p1 = p1 -1; p3 = p3 + 1; printf("Firing a\n");}

     :: atomic{p2 >= 1 -> p2 = p2 -1; p4 = p4 + 1; printf("Firing b\n");}

     :: atomic{p3 >= 1 && p4  >= 1 -> p3 = p3 -1; p4 = p4 - 1; p5 = p5 + 1; printf("Firing c\n");}

     :: atomic{p5 >= 2 -> p5 = p5 -2; p1 = p1 + 1; p2 = p2 + 1; printf("Firing d\n");}

od;

}
