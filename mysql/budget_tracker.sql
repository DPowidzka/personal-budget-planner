-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sty 04, 2025 at 12:28 AM
-- Wersja serwera: 8.4.0
-- Wersja PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `budget_tracker`
--

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `accounts`
--

CREATE TABLE `accounts` (
  `account_id` int NOT NULL,
  `account_type_id` int DEFAULT NULL,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `current_balance` decimal(12,2) NOT NULL,
  `is_credit` tinyint(1) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `accounts`
--

INSERT INTO `accounts` (`account_id`, `account_type_id`, `name`, `current_balance`, `is_credit`) VALUES
(1, 1, 'Oszczędności', 24816.00, 0),
(2, 2, 'Bieżące', 3600.00, 0),
(3, 3, 'Karta kredytowa', -920.00, 1),
(4, 4, 'Gotówka', 2480.00, 0),
(5, 5, 'Kredyt na samochód', -21600.00, 1);

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `accounttypes`
--

CREATE TABLE `accounttypes` (
  `account_type_id` int NOT NULL,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `accounttypes`
--

INSERT INTO `accounttypes` (`account_type_id`, `name`) VALUES
(1, 'Oszczędności'),
(2, 'Bieżące'),
(3, 'Karta kredytowa'),
(4, 'Gotówka'),
(5, 'Kredyt');

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `categories`
--

CREATE TABLE `categories` (
  `category_id` int NOT NULL,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `icon_type` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `categories`
--

INSERT INTO `categories` (`category_id`, `name`, `icon_type`, `is_active`) VALUES
(1, 'Wynajem', 'home', 1),
(2, 'Produkty spożywcze', 'shopping-cart', 1),
(3, 'Podróż', 'plane', 1),
(4, 'Restauracja', 'utensils', 1),
(5, 'Siłownia', 'dumbbell', 1),
(6, 'Pensja', 'money-bill', 1),
(7, 'Bonus', 'gift', 1),
(8, 'Parents', 'users', 1),
(9, 'Internet', 'wifi', 1),
(10, 'Oszczędności', 'piggy-bank', 1);

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `transactions`
--

CREATE TABLE `transactions` (
  `transaction_id` int NOT NULL,
  `account_id` int DEFAULT NULL,
  `category_id` int DEFAULT NULL,
  `transaction_type_id` int DEFAULT NULL,
  `amount` decimal(12,2) NOT NULL,
  `transaction_date` date NOT NULL,
  `description` text COLLATE utf8mb4_unicode_ci,
  `is_recurring` tinyint(1) DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `transactions`
--

INSERT INTO `transactions` (`transaction_id`, `account_id`, `category_id`, `transaction_type_id`, `amount`, `transaction_date`, `description`, `is_recurring`) VALUES
(1, 1, 6, 2, 6616.00, '2024-11-01', 'Pensja', 0),
(2, 1, 7, 2, 2240.00, '2024-12-31', 'Bonus', 0),
(3, 2, 8, 2, 960.00, '2024-11-17', 'Parents', 0),
(4, 3, 1, 1, 1600.00, '2024-12-05', 'Wynajem', 0),
(5, 3, 2, 1, 1000.00, '2024-11-02', 'Produkty spożywcze', 0),
(6, 3, 3, 1, 600.00, '2024-11-04', 'Podróż', 0),
(7, 3, 4, 1, 160.00, '2024-11-04', 'Restauracja', 0),
(8, 3, 4, 1, 160.00, '2024-12-02', 'Restauracja', 0);

-- --------------------------------------------------------

--
-- Struktura tabeli dla tabeli `transactiontypes`
--

CREATE TABLE `transactiontypes` (
  `transaction_type_id` int NOT NULL,
  `name` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `transactiontypes`
--

INSERT INTO `transactiontypes` (`transaction_type_id`, `name`) VALUES
(1, 'WYDATEK'),
(2, 'DOCHÓD');

--
-- Indeksy dla zrzutów tabel
--

--
-- Indeksy dla tabeli `accounts`
--
ALTER TABLE `accounts`
  ADD PRIMARY KEY (`account_id`),
  ADD KEY `account_type_id` (`account_type_id`);

--
-- Indeksy dla tabeli `accounttypes`
--
ALTER TABLE `accounttypes`
  ADD PRIMARY KEY (`account_type_id`);

--
-- Indeksy dla tabeli `categories`
--
ALTER TABLE `categories`
  ADD PRIMARY KEY (`category_id`);

--
-- Indeksy dla tabeli `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`transaction_id`),
  ADD KEY `account_id` (`account_id`),
  ADD KEY `category_id` (`category_id`),
  ADD KEY `transaction_type_id` (`transaction_type_id`);

--
-- Indeksy dla tabeli `transactiontypes`
--
ALTER TABLE `transactiontypes`
  ADD PRIMARY KEY (`transaction_type_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `accounts`
--
ALTER TABLE `accounts`
  MODIFY `account_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `accounttypes`
--
ALTER TABLE `accounttypes`
  MODIFY `account_type_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `categories`
--
ALTER TABLE `categories`
  MODIFY `category_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;

--
-- AUTO_INCREMENT for table `transactions`
--
ALTER TABLE `transactions`
  MODIFY `transaction_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `transactiontypes`
--
ALTER TABLE `transactiontypes`
  MODIFY `transaction_type_id` int NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `accounts`
--
ALTER TABLE `accounts`
  ADD CONSTRAINT `accounts_ibfk_1` FOREIGN KEY (`account_type_id`) REFERENCES `accounttypes` (`account_type_id`);

--
-- Constraints for table `transactions`
--
ALTER TABLE `transactions`
  ADD CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`account_id`),
  ADD CONSTRAINT `transactions_ibfk_2` FOREIGN KEY (`category_id`) REFERENCES `categories` (`category_id`),
  ADD CONSTRAINT `transactions_ibfk_3` FOREIGN KEY (`transaction_type_id`) REFERENCES `transactiontypes` (`transaction_type_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
