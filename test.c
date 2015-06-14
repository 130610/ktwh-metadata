#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <ctype.h>
#include <cddb/cddb.h>

cddb_conn_t *init_conn();
cddb_disc_t *init_disc();
void read_db(cddb_conn_t *conn, cddb_disc_t *disc);
int search_db(cddb_conn_t *conn, cddb_disc_t *disc, const char *str);
void lowercase(char *str);

int main(int argc, char *argv[]) {
	/*initialize the connection to the freedb server */
	cddb_conn_t *conn = NULL;
	cddb_disc_t *disc;
	conn = init_conn();

	/* set track info */
	printf("argc: %d\n", argc);
	if (argc != 3) {
		fprintf(stderr, "usage: cddb_query <discid> <category>\n");
		return -1;
	}
	char *p;
	unsigned long discid = strtoul(argv[1], &p, 16);
	char *cat = argv[2];
	lowercase(cat);

	/* initialize the disc */
	disc = init_disc();
	cddb_disc_set_discid(disc, discid);
	cddb_disc_set_category_str(disc, cat);

	/* query the database to populate the disc info */
	read_db(conn, disc);

	/* format an output track info */
	const char *artist = cddb_disc_get_artist(disc);
	const char *album = cddb_disc_get_title(disc);
	unsigned int date = cddb_disc_get_year(disc);
	const char *label = "";
	const char *genre = cddb_disc_get_genre(disc);
	printf("%s\t%s\t%d\t%s\t%s\n", artist, album, date, label, genre);

	return 0;
}

/* initialize connection to cddb server */
cddb_conn_t *init_conn() {
	cddb_conn_t *conn;
	if ((conn = cddb_new()) == NULL) {
		fprintf(stderr, "out of memory, "
	                "unable to create connection structure");
	}

	/* HTTP settings */
	cddb_http_enable(conn);
	cddb_set_server_port(conn, 80);
	cddb_set_server_name(conn, "freedb.org");
	cddb_set_http_path_query(conn, "/~cddb/cddb.cgi");
	cddb_set_http_path_submit(conn, "/~cddb/submit.cgi");

	return conn;
}

/* initialize disc */
cddb_disc_t *init_disc() {
	cddb_disc_t *disc;
	if ((disc = cddb_disc_new()) == NULL) {
	    fprintf(stderr, "out of memory, unable to create disc");
	    exit(-1);
	}

	return disc;
}

/* read data from cddb database */
void read_db(cddb_conn_t *conn, cddb_disc_t *disc) {
	int success = cddb_read(conn, disc);
	if (!success) {
	    /* something went wrong, print error */
	    cddb_error_print(cddb_errno(conn));
	    exit(-1);
	}
}

/* change all characters in a string to lowercase (for cddb_read call in main) */
void lowercase(char *str) {
	for (int i = 0; str[i] != '\0'; i++) {
		tolower(str[i]);
		str[i] = tolower(str[i]);
	}
}
