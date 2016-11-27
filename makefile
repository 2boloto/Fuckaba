MEMORY_LENGTH=380633088

fuckaba.bf: fuckaba.txt preprocessor.py lib/*.txt resources/*.bin
	echo "#!interpreter -l" $(MEMORY_LENGTH) > $@
	echo "+" >> $@
	./preprocessor.py $< >> $@

fuckaba: fuckaba.c

fuckaba.c: fuckaba.bf Brainfuck-tools/translator.py
	Brainfuck-tools/translator.py -m $(MEMORY_LENGTH) -d $< > $@

clean:
	rm -f fuckaba fuckaba.c

resources/index.bin: resources/index-head.txt resources/index-body.htm
	echo | cat $< - | sed "s/$$/\r/g" | cat - resources/index-body.htm > $@

resources/redirect.bin: resources/redirect-head.txt
	echo | cat $< - | sed "s/$$/\r/g" > $@
