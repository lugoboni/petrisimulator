#define R 4
#define C 5
typedef VECTOR {
   byte vector[C];
};
VECTOR pre_matrix[R];
VECTOR post_matrix[R];

byte token_list[2];
byte token_number = 2;

byte places_initial[C];
byte transitions_initial[R];

active proctype P(){

   pre_matrix[0].vector[0] = 0;
   pre_matrix[0].vector[1] = 0;
   pre_matrix[0].vector[2] = 0;
   pre_matrix[0].vector[3] = 0;
   pre_matrix[0].vector[4] = 2;
   pre_matrix[1].vector[0] = 1;
   pre_matrix[1].vector[1] = 0;
   pre_matrix[1].vector[2] = 0;
   pre_matrix[1].vector[3] = 0;
   pre_matrix[1].vector[4] = 0;
   pre_matrix[2].vector[0] = 0;
   pre_matrix[2].vector[1] = 1;
   pre_matrix[2].vector[2] = 0;
   pre_matrix[2].vector[3] = 0;
   pre_matrix[2].vector[4] = 0;
   pre_matrix[3].vector[0] = 0;
   pre_matrix[3].vector[1] = 0;
   pre_matrix[3].vector[2] = 1;
   pre_matrix[3].vector[3] = 1;
   pre_matrix[3].vector[4] = 0;
   post_matrix[0].vector[0] = 0;
   post_matrix[0].vector[1] = 1;
   post_matrix[0].vector[2] = 0;
   post_matrix[0].vector[3] = 0;
   post_matrix[0].vector[4] = 0;
   post_matrix[1].vector[0] = 0;
   post_matrix[1].vector[1] = 0;
   post_matrix[1].vector[2] = 1;
   post_matrix[1].vector[3] = 0;
   post_matrix[1].vector[4] = 0;
   post_matrix[2].vector[0] = 0;
   post_matrix[2].vector[1] = 0;
   post_matrix[2].vector[2] = 0;
   post_matrix[2].vector[3] = 1;
   post_matrix[2].vector[4] = 0;
   post_matrix[3].vector[0] = 0;
   post_matrix[3].vector[1] = 0;
   post_matrix[3].vector[2] = 0;
   post_matrix[3].vector[3] = 0;
   post_matrix[3].vector[4] = 2;

   places_initial[0] = 1;
   places_initial[1] = 1;
   places_initial[2] = 0;
   places_initial[3] = 0;
   places_initial[4] = 0;

   int count_c = C - 1;
   int count_r = R - 1;

   byte temp_places[C];
   byte temp_transitions[R];

   VECTOR copy_post[R];
   byte fired = 0;
   byte started = 0;

   do
   :: fired == 0 && started == 1 -> 
      printf("Teminado \n\n");
      break;
   :: else ->
      started = 1;
      do
      :: count_c == -1 -> 
         temp_places[0] = 0;
         temp_places[1] = 0;
         temp_places[2] = 0;
         temp_places[3] = 0;
         temp_places[4] = 0;
         count_c = C - 1;
         count_r = R - 1;
         break;
      :: else ->
         count_r = R - 1;
         do
         :: count_r > -1 ->
               if
               :: pre_matrix[count_r].vector[count_c] != 0 && places_initial[count_c] > 0->
                  if
                  :: pre_matrix[count_r].vector[count_c] >= places_initial[count_c] ->
                     temp_transitions[count_r] = temp_transitions[count_r] + places_initial[count_c];
                     printf("%d tokens movido do lugar %d para transição %d\n", places_initial[count_c], count_c, count_r);
                     places_initial[count_c] = 0;
                  :: pre_matrix[count_r].vector[count_c] < places_initial[count_c] ->
                     temp_transitions[count_r] = temp_transitions[count_r] + pre_matrix[count_r].vector[count_c];
                     byte temp_diff = places_initial[count_c] - pre_matrix[count_r].vector[count_c];
                     places_initial[count_c] = temp_diff;
                     printf("%d tokens movido do lugar %d para transição %d\n", temp_diff, count_c, count_r);
                  :: else -> printf(".");
                  fi;
               :: else -> printf(".");
               fi;
               count_r = count_r - 1;
         :: else -> break;
         od;
         count_c = count_c - 1;
      od;



      copy_post[0].vector[0] = post_matrix[0].vector[0] ;
      copy_post[0].vector[1] = post_matrix[0].vector[1] ;
      copy_post[0].vector[2] = post_matrix[0].vector[2] ;
      copy_post[0].vector[3] = post_matrix[0].vector[3] ;
      copy_post[0].vector[4] = post_matrix[0].vector[4] ;
      copy_post[1].vector[0] = post_matrix[1].vector[0] ;
      copy_post[1].vector[1] = post_matrix[1].vector[1] ;
      copy_post[1].vector[2] = post_matrix[1].vector[2] ;
      copy_post[1].vector[3] = post_matrix[1].vector[3] ;
      copy_post[1].vector[4] = post_matrix[1].vector[4] ;
      copy_post[2].vector[0] = post_matrix[2].vector[0] ;
      copy_post[2].vector[1] = post_matrix[2].vector[1] ;
      copy_post[2].vector[2] = post_matrix[2].vector[2] ;
      copy_post[2].vector[3] = post_matrix[2].vector[3] ;
      copy_post[2].vector[4] = post_matrix[2].vector[4] ;
      copy_post[3].vector[0] = post_matrix[3].vector[0] ;
      copy_post[3].vector[1] = post_matrix[3].vector[1] ;
      copy_post[3].vector[2] = post_matrix[3].vector[2] ;
      copy_post[3].vector[3] = post_matrix[3].vector[3] ;
      copy_post[3].vector[4] = post_matrix[3].vector[4] ;
      fired = 0;


      do
      :: count_c == -1 -> 
         temp_transitions[0] = 0;
         temp_transitions[1] = 0;
         temp_transitions[2] = 0;
         temp_transitions[3] = 0;
         places_initial[0] = temp_places[0];
         places_initial[1] = temp_places[1];
         places_initial[2] = temp_places[2];
         places_initial[3] = temp_places[3];
         places_initial[4] = temp_places[4];
         count_c = C - 1;
         count_r = R - 1;
         break;
      :: else ->
         count_r = R - 1;
         do
         :: count_r > -1 ->
               if
               :: copy_post[count_r].vector[count_c] != 0 && temp_transitions[count_r] > 0->
                  if
                  :: copy_post[count_r].vector[count_c] >= temp_transitions[count_r] ->

                     temp_places[count_c] = temp_places[count_c] + temp_transitions[count_r];
                     copy_post[count_r].vector[count_c] = copy_post[count_r].vector[count_c] - temp_transitions[count_r];
                     if
                     :: copy_post[count_r].vector[count_c] == 0 -> 
                        fired = fired + 1;
                        printf("tokens movido da transição %d para o lugar %d\n", count_r, count_c);
                     fi;                  
                     temp_transitions[count_r] = 0;

                  :: copy_post[count_r].vector[count_c] < temp_transitions[count_r] ->

                     temp_places[count_c] = temp_places[count_c] + copy_post[count_r].vector[count_c];
                     copy_post[count_r].vector[count_c] = 0;
                     fired = fired + 1;
                     printf("tokens movido da transição %d para o lugar %d\n", count_r, count_c);
                     temp_diff = temp_transitions[count_r] - copy_post[count_r].vector[count_c];
                     temp_transitions[count_r] = temp_diff;

                  :: else -> printf(".");
                  fi;
               :: else -> printf(".");
               fi;
               count_r = count_r - 1;
         :: else -> break;
         od;
         count_c = count_c - 1;
      od;

   od;


}
