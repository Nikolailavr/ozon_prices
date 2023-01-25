create table users (
	telegram_id bigint primary key not null,
	last_command varchar(30) DEFAULT ""
);

create table links (
	telegram_id bigint not null,
	url_link text not null,
	FOREIGN KEY (telegram_id) REFERENCES users (telegram_id)
);

create table prices (
	url_link text primary key not null,
	price int not null DEFAULT 0,
	FOREIGN KEY (url_link) REFERENCES links (url_link)
);
