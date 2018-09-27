active proctype P() {
byte p1 = 1;
byte p2 = 1;
byte p3 = 0;
byte p4 = 0;
byte p5 = 0;
do::atomic{p1 >= 1 -> p1 = p1 - 1; p3 = p3 + 1; printf("\nFiring a ->  Places status: p1 = %d p2 = %d p3 = %d p4 = %d p5 = %d", p1, p2, p3, p4, p5);}
  ::atomic{p3 >= 1 && p4 >= 1 -> p3 = p3 - 1; p4 = p4 - 1; p5 = p5 + 1; printf("\nFiring c ->  Places status: p1 = %d p2 = %d p3 = %d p4 = %d p5 = %d", p1, p2, p3, p4, p5);}
  ::atomic{p2 >= 1 -> p2 = p2 - 1; p4 = p4 + 1; printf("\nFiring b ->  Places status: p1 = %d p2 = %d p3 = %d p4 = %d p5 = %d", p1, p2, p3, p4, p5);}
od}
