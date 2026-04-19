fn control_flow_demo(mut n:i32) {
  if n > 10 {
    n = n - 1;
  } else if n == 10 {
    n = n + 1;
  } else {
    n = n + 2;
  }

  while n < 20 {
    n = n + 1;
    if n == 15 {
      continue;
    }
  }

  loop {
    if n > 25 {
      break;
    }
    n = n + 1;
  }

  for i in 0..10 {
    if i == 3 {
      continue;
    }
    if i > 7 {
      break;
    }
  }
}
