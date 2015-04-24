#map_synset_versions.py -if $1-il WordNet-eng171 -iv 171 -of $2 -ov 30 -ol WordNet-eng30

for sv2file in ../senseval2/*
do
  map_synset_versions.py -if $sv2file -ir WordNet-eng171 -iv 171 -of $sv2file.mapped -ov 30 -or WordNet-eng30
  mv $sv2file.mapped $sv2file
  echo Done $sv2file
done
