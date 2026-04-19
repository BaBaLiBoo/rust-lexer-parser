fn advanced_expr_demo(mut a:i32, mut p:i32, mut arr:i32) {
  &a;
  *p + 1;

  [];
  [1,2,3];
  arr[0];
  foo([1,2], arr[0]);

  (a);
  (1,2);
  (a, arr[0] + 1);
  ((1,2), (3,4));
}
