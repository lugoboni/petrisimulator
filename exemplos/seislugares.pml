active proctype P() {
byte p1 = 1;
byte p2 = 1;
byte p3 = 0;
byte p5 = 0;
byte p4 = 0;
byte p6 = 0;
do::atomic{p4 >= 1 && p3 >= 1 -> p4 = p4 - 1; p3 = p3 - 1; p5 = p5 + 2; printf("Firing c\n");}
  ::atomic{p2 >= 1 -> p2 = p2 - 1; p4 = p4 + 1; printf("Firing b\n");}
  ::atomic{p1 >= 1 -> p1 = p1 - 1; p3 = p3 + 1; printf("Firing a\n");}
  ::atomic{p6 >= 1 -> p6 = p6 - 1; p1 = p1 + 1; p2 = p2 + 1; printf("Firing d\n");}
od}
