CREATE TABLE log_date
(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	entry_date DATE NOT NULL
);

CREATE TABLE food
(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	proteins INT NOT NULL,
	carbs INT NOT NULL,
	fats INT NOT NULL,
	calories INT NOT NULL
);

CREATE TABLE food_date
(
	food_id INTEGER NOT NULL,
	log_date_id INTEGER NOT NULL,
	PRIMARY KEY (food_id, log_date_id)
);