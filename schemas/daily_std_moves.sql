CREATE TABLE `daily_std_moves` (
  `date` date NOT NULL,
  `high` decimal(10,2) DEFAULT NULL,
  `low` decimal(10,2) DEFAULT NULL,
  `std` decimal(10,2) DEFAULT NULL,
  `low_to_high` decimal(10,2) DEFAULT NULL,
  `prev_low_to_high` decimal(10,2) DEFAULT NULL,
  `prev_high_to_low` decimal(10,2) DEFAULT NULL,
  PRIMARY KEY (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1
