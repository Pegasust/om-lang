// pub struct BootmapIterator<It, T, B, F>
// where
//     It: Iterator<Item = T>,
//     F: Fn(T, B) -> (T, B),
// {
//     base_iter: It,
//     bootstrap: B,
//     map_fn: F,
// }
//
// impl<'a, It, T, B, F> Iterator for BootmapIterator<It, T, B, F>
// where
//     It: Iterator<Item = T>,
//     F: Fn(T, B) -> (T, B),
//     B: 'a,
// {
//     type Item = (T, &'a B);
//
//     fn next(&'a mut self) -> Option<Self::Item> {
//         let base = self.base_iter.next()?;
//         let mut v = self.map_fn(base, self.bootstrap);
//         self.bootstrap = v.1;
//         (v.0, &self.boot_strap)
//     }
// }

// /// Returns an iterator that performs map with some bootstrapping value
// pub fn bootmap<It, T, B, F>(iter: It, map_fn: F, bootstrap: B)
// -> impl Iterator<Item=(T, B)>
// where It: Iterator<Item=T>, F: Fn((T, B))->(T, B),
//
// {
//     let mut my_bootstrap = bootstrap;
//     iter.map(|v| map_fn)
// }
