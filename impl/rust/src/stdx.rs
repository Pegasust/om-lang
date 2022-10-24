
pub struct BootmapIterator {}

/// Returns an iterator that performs map with some bootstrapping value
pub fn bootmap<It, T, B, F>(iter: It, map_fn: F, bootstrap: B) 
-> impl Iterator<Item=(T, B)>
where It: Iterator<Item=T>, F: Fn((T, B))->(T, B)
{
    iter.map(|v| (v, bootstrap)).map(|(v, b)| map_fn((v, b)))
}
