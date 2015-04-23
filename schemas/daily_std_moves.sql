CREATE TABLE `daily_std_moves` (
  `date` date NOT NULL,
  `low_to_high` float(10,2) DEFAULT NULL,
  `prev_low_to_high` float(10,2) DEFAULT NULL,
  `prev_high_to_low` float(10,2) DEFAULT NULL,
  PRIMARY KEY (`date`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1
