# Copyright 2012 Seth VanHeulen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
