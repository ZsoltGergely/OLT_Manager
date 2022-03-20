-- phpMyAdmin SQL Dump
-- version 5.1.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Mar 20, 2022 at 08:56 PM
-- Server version: 10.4.22-MariaDB
-- PHP Version: 7.4.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `olt_management`
--

-- --------------------------------------------------------

--
-- Table structure for table `cards`
--

CREATE TABLE `cards` (
  `id` int(11) NOT NULL,
  `olt_id` int(11) NOT NULL,
  `olt_slot` int(11) NOT NULL,
  `type` tinyint(4) NOT NULL,
  `type_name` char(8) NOT NULL,
  `uplink_ports` int(11) DEFAULT NULL,
  `pon_ports` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `clients`
--

CREATE TABLE `clients` (
  `id` int(11) NOT NULL,
  `name` char(64) NOT NULL,
  `address` char(128) DEFAULT NULL,
  `device_type` int(11) NOT NULL,
  `config` char(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `device_types`
--

CREATE TABLE `device_types` (
  `id` int(11) NOT NULL,
  `name` int(11) NOT NULL,
  `nr_ports` tinyint(4) NOT NULL,
  `router` tinyint(1) NOT NULL,
  `wifi` tinyint(1) NOT NULL,
  `def_config` char(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `olts`
--

CREATE TABLE `olts` (
  `id` int(11) NOT NULL,
  `name` char(64) NOT NULL,
  `ip` char(24) NOT NULL,
  `telnet_user` char(24) NOT NULL,
  `telnet_pass` char(24) NOT NULL,
  `telnet_port` int(11) NOT NULL,
  `r_community` char(24) DEFAULT NULL,
  `rw_community` char(24) DEFAULT NULL,
  `snmp_port` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `onu_vports`
--

CREATE TABLE `onu_vports` (
  `id` int(11) NOT NULL,
  `pon_port_id` int(11) NOT NULL,
  `vport_number` tinyint(3) UNSIGNED NOT NULL,
  `client_id` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `pon_ports`
--

CREATE TABLE `pon_ports` (
  `id` int(11) NOT NULL,
  `port_nr` int(11) NOT NULL,
  `card_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `cards`
--
ALTER TABLE `cards`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `clients`
--
ALTER TABLE `clients`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `name` (`name`);

--
-- Indexes for table `device_types`
--
ALTER TABLE `device_types`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `olts`
--
ALTER TABLE `olts`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `onu_vports`
--
ALTER TABLE `onu_vports`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `pon_ports`
--
ALTER TABLE `pon_ports`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `cards`
--
ALTER TABLE `cards`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `clients`
--
ALTER TABLE `clients`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `device_types`
--
ALTER TABLE `device_types`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `olts`
--
ALTER TABLE `olts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `onu_vports`
--
ALTER TABLE `onu_vports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `pon_ports`
--
ALTER TABLE `pon_ports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
