cd "$SRC"/dateparser
pip3 install .

# Build fuzzers in $OUT
for fuzzer in $(find fuzzing -name '*_fuzzer.py');do
  compile_python_fuzzer "$fuzzer" --add-binary="dateparser/data:dateparser/data"
done
zip -q $OUT/dateparser_fuzzer_seed_corpus.zip $SRC/corpus/*
