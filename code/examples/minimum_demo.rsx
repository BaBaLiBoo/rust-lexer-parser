fn add_one(mut v:i32) -> i32 {
  return v + 1;
}

fn minimum_demo(mut a:i32) -> i32 {
  ;
  let mut x:i32 = 1;
  let mut y;
  y = add_one(x);
  if a > 0 {
    return y;
  }
  while a < 3 {
    a = a + 1;
  }
  return a;
}
