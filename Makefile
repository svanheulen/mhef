TARGETS=data_decrypt quest_decrypt savedata_decrypt

all: $(TARGETS)

data_decrypt: data_example.c data.c
	gcc $^ -o $@

quest_decrypt: quest_example.c quest.c
	gcc $^ -o $@ -lcrypto

savedata_decrypt: savedata_example.c savedata.c
	gcc $^ -o $@ -lcrypto

.PHONY: clean

clean:
	rm -rf $(TARGETS)
