all: query_freedb

query_freedb: query_freedb.c
	gcc -std=c99 -o query_freedb query_freedb.c -lcddb
