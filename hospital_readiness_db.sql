-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Aug 09, 2026 at 07:20 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `hospital_readiness_db`
--

-- --------------------------------------------------------

--
-- Table structure for table `tbl_checklist_items`
--

CREATE TABLE `tbl_checklist_items` (
  `id` int(11) NOT NULL,
  `scheduled_procedure_id` int(11) NOT NULL,
  `task_name` varchar(100) NOT NULL,
  `task_type` enum('patient_action','staff_verification','document_upload') NOT NULL,
  `description` text DEFAULT NULL,
  `due_by_datetime` datetime NOT NULL,
  `is_critical` tinyint(1) NOT NULL DEFAULT 0,
  `status` enum('pending','completed','verified','failed') NOT NULL DEFAULT 'pending',
  `completed_by_user_id` int(11) DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL,
  `verified_by_user_id` int(11) DEFAULT NULL,
  `verified_at` datetime DEFAULT NULL,
  `notes` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tbl_checklist_items`
--

INSERT INTO `tbl_checklist_items` (`id`, `scheduled_procedure_id`, `task_name`, `task_type`, `description`, `due_by_datetime`, `is_critical`, `status`, `completed_by_user_id`, `completed_at`, `verified_by_user_id`, `verified_at`, `notes`) VALUES
(1, 1, 'NPO Fasting (No food or water)', 'patient_action', 'Fasting is required for at least 8 hours prior to the heart catheterization.', '2026-09-24 01:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(2, 1, 'Stop Anticoagulant (Blood Thinners)', 'patient_action', 'Temporarily suspend blood thinning medications 48 hours prior to procedure as advised by physician.', '2026-09-22 09:00:00', 1, 'completed', NULL, NULL, NULL, NULL, NULL),
(3, 1, 'Upload Recent ECG Lab Report', 'document_upload', 'Please upload a PDF or image copy of your 12-lead ECG conducted in the last 14 days.', '2026-09-21 17:00:00', 1, 'pending', 4, '2026-09-21 17:00:00', NULL, NULL, NULL),
(4, 1, 'Clinical Consent Form Signature', 'patient_action', 'Verify that the physical surgical consent documentation has been signed by patient and surgeon.', '2026-09-24 08:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(5, 2, 'Liquid Prep Diet Compliance', 'patient_action', 'Complete gastroenterologist-approved colon cleansing prep formulation.', '2026-09-24 18:00:00', 1, 'completed', 5, '2026-09-24 18:00:00', NULL, NULL, NULL),
(6, 2, 'Confirm Escort Driver Present', 'patient_action', 'Provide details of the responsible adult driving you home after sedation.', '2026-09-25 10:30:00', 0, 'pending', NULL, NULL, NULL, NULL, NULL),
(353, 9, 'Complete fasting instructions', 'patient_action', 'Follow the fasting instructions provided for the procedure.', '2026-09-26 01:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(354, 10, 'Complete fasting instructions', 'patient_action', 'Follow the fasting instructions provided for the procedure.', '2026-09-28 02:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(355, 11, 'Complete fasting instructions', 'patient_action', 'Follow the fasting instructions provided for the procedure.', '2026-09-29 03:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(356, 12, 'Complete fasting instructions', 'patient_action', 'Follow the fasting instructions provided for the procedure.', '2026-09-30 06:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(357, 13, 'Complete fasting instructions', 'patient_action', 'Follow the fasting instructions provided for the procedure.', '2026-10-02 01:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(358, 14, 'Complete fasting instructions', 'patient_action', 'Follow the fasting instructions provided for the procedure.', '2026-10-05 02:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(359, 15, 'Complete fasting instructions', 'patient_action', 'Follow the fasting instructions provided for the procedure.', '2026-10-09 00:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(360, 19, 'Complete fasting instructions', 'patient_action', 'Follow the fasting instructions provided for the procedure.', '2026-10-26 01:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(361, 16, 'Complete fasting instructions', 'patient_action', 'Follow the fasting instructions provided for the procedure.', '2026-10-14 05:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(362, 20, 'Complete fasting instructions', 'patient_action', 'Follow the fasting instructions provided for the procedure.', '2026-10-29 02:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(363, 17, 'Complete fasting instructions', 'patient_action', 'Follow the fasting instructions provided for the procedure.', '2026-10-19 03:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(364, 21, 'Complete fasting instructions', 'patient_action', 'Follow the fasting instructions provided for the procedure.', '2026-11-03 06:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(365, 18, 'Complete fasting instructions', 'patient_action', 'Follow the fasting instructions provided for the procedure.', '2026-10-22 07:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(366, 22, 'Complete fasting instructions', 'patient_action', 'Follow the fasting instructions provided for the procedure.', '2026-11-06 03:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(367, 23, 'Complete fasting instructions', 'patient_action', 'Follow the fasting instructions provided for the procedure.', '2026-11-10 01:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(368, 24, 'Complete fasting instructions', 'patient_action', 'Follow the fasting instructions provided for the procedure.', '2026-11-13 07:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(369, 25, 'Complete fasting instructions', 'patient_action', 'Follow the fasting instructions provided for the procedure.', '2026-11-17 00:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(370, 26, 'Complete fasting instructions', 'patient_action', 'Follow the fasting instructions provided for the procedure.', '2026-11-20 02:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(371, 27, 'Complete fasting instructions', 'patient_action', 'Follow the fasting instructions provided for the procedure.', '2026-11-24 05:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(372, 28, 'Complete fasting instructions', 'patient_action', 'Follow the fasting instructions provided for the procedure.', '2026-11-27 08:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(373, 9, 'Upload required blood test report', 'document_upload', 'Upload the latest required blood test report before the procedure.', '2026-09-25 09:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(374, 10, 'Upload required blood test report', 'document_upload', 'Upload the latest required blood test report before the procedure.', '2026-09-27 10:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(375, 11, 'Upload required blood test report', 'document_upload', 'Upload the latest required blood test report before the procedure.', '2026-09-28 11:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(376, 12, 'Upload required blood test report', 'document_upload', 'Upload the latest required blood test report before the procedure.', '2026-09-29 14:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(377, 13, 'Upload required blood test report', 'document_upload', 'Upload the latest required blood test report before the procedure.', '2026-10-01 09:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(378, 14, 'Upload required blood test report', 'document_upload', 'Upload the latest required blood test report before the procedure.', '2026-10-04 10:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(379, 15, 'Upload required blood test report', 'document_upload', 'Upload the latest required blood test report before the procedure.', '2026-10-08 08:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(380, 19, 'Upload required blood test report', 'document_upload', 'Upload the latest required blood test report before the procedure.', '2026-10-25 09:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(381, 16, 'Upload required blood test report', 'document_upload', 'Upload the latest required blood test report before the procedure.', '2026-10-13 13:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(382, 20, 'Upload required blood test report', 'document_upload', 'Upload the latest required blood test report before the procedure.', '2026-10-28 10:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(383, 17, 'Upload required blood test report', 'document_upload', 'Upload the latest required blood test report before the procedure.', '2026-10-18 11:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(384, 21, 'Upload required blood test report', 'document_upload', 'Upload the latest required blood test report before the procedure.', '2026-11-02 14:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(385, 18, 'Upload required blood test report', 'document_upload', 'Upload the latest required blood test report before the procedure.', '2026-10-21 15:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(386, 22, 'Upload required blood test report', 'document_upload', 'Upload the latest required blood test report before the procedure.', '2026-11-05 11:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(387, 23, 'Upload required blood test report', 'document_upload', 'Upload the latest required blood test report before the procedure.', '2026-11-09 09:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(388, 24, 'Upload required blood test report', 'document_upload', 'Upload the latest required blood test report before the procedure.', '2026-11-12 15:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(389, 25, 'Upload required blood test report', 'document_upload', 'Upload the latest required blood test report before the procedure.', '2026-11-16 08:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(390, 26, 'Upload required blood test report', 'document_upload', 'Upload the latest required blood test report before the procedure.', '2026-11-19 10:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(391, 27, 'Upload required blood test report', 'document_upload', 'Upload the latest required blood test report before the procedure.', '2026-11-23 13:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(392, 28, 'Upload required blood test report', 'document_upload', 'Upload the latest required blood test report before the procedure.', '2026-11-26 16:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(393, 9, 'Upload consent form', 'document_upload', 'Upload the signed consent form required for the procedure.', '2026-09-25 21:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(394, 10, 'Upload consent form', 'document_upload', 'Upload the signed consent form required for the procedure.', '2026-09-27 22:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(395, 11, 'Upload consent form', 'document_upload', 'Upload the signed consent form required for the procedure.', '2026-09-28 23:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(396, 12, 'Upload consent form', 'document_upload', 'Upload the signed consent form required for the procedure.', '2026-09-30 02:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(397, 13, 'Upload consent form', 'document_upload', 'Upload the signed consent form required for the procedure.', '2026-10-01 21:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(398, 14, 'Upload consent form', 'document_upload', 'Upload the signed consent form required for the procedure.', '2026-10-04 22:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(399, 15, 'Upload consent form', 'document_upload', 'Upload the signed consent form required for the procedure.', '2026-10-08 20:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(400, 19, 'Upload consent form', 'document_upload', 'Upload the signed consent form required for the procedure.', '2026-10-25 21:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(401, 16, 'Upload consent form', 'document_upload', 'Upload the signed consent form required for the procedure.', '2026-10-14 01:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(402, 20, 'Upload consent form', 'document_upload', 'Upload the signed consent form required for the procedure.', '2026-10-28 22:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(403, 17, 'Upload consent form', 'document_upload', 'Upload the signed consent form required for the procedure.', '2026-10-18 23:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(404, 21, 'Upload consent form', 'document_upload', 'Upload the signed consent form required for the procedure.', '2026-11-03 02:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(405, 18, 'Upload consent form', 'document_upload', 'Upload the signed consent form required for the procedure.', '2026-10-22 03:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(406, 22, 'Upload consent form', 'document_upload', 'Upload the signed consent form required for the procedure.', '2026-11-05 23:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(407, 23, 'Upload consent form', 'document_upload', 'Upload the signed consent form required for the procedure.', '2026-11-09 21:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(408, 24, 'Upload consent form', 'document_upload', 'Upload the signed consent form required for the procedure.', '2026-11-13 03:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(409, 25, 'Upload consent form', 'document_upload', 'Upload the signed consent form required for the procedure.', '2026-11-16 20:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(410, 26, 'Upload consent form', 'document_upload', 'Upload the signed consent form required for the procedure.', '2026-11-19 22:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(411, 27, 'Upload consent form', 'document_upload', 'Upload the signed consent form required for the procedure.', '2026-11-24 01:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(412, 28, 'Upload consent form', 'document_upload', 'Upload the signed consent form required for the procedure.', '2026-11-27 04:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(413, 9, 'Complete medication instructions', 'patient_action', 'Follow the medication instructions given by the doctor before the procedure.', '2026-09-25 21:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(414, 10, 'Complete medication instructions', 'patient_action', 'Follow the medication instructions given by the doctor before the procedure.', '2026-09-27 22:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(415, 11, 'Complete medication instructions', 'patient_action', 'Follow the medication instructions given by the doctor before the procedure.', '2026-09-28 23:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(416, 12, 'Complete medication instructions', 'patient_action', 'Follow the medication instructions given by the doctor before the procedure.', '2026-09-30 02:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(417, 13, 'Complete medication instructions', 'patient_action', 'Follow the medication instructions given by the doctor before the procedure.', '2026-10-01 21:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(418, 14, 'Complete medication instructions', 'patient_action', 'Follow the medication instructions given by the doctor before the procedure.', '2026-10-04 22:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(419, 15, 'Complete medication instructions', 'patient_action', 'Follow the medication instructions given by the doctor before the procedure.', '2026-10-08 20:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(420, 19, 'Complete medication instructions', 'patient_action', 'Follow the medication instructions given by the doctor before the procedure.', '2026-10-25 21:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(421, 16, 'Complete medication instructions', 'patient_action', 'Follow the medication instructions given by the doctor before the procedure.', '2026-10-14 01:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(422, 20, 'Complete medication instructions', 'patient_action', 'Follow the medication instructions given by the doctor before the procedure.', '2026-10-28 22:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(423, 17, 'Complete medication instructions', 'patient_action', 'Follow the medication instructions given by the doctor before the procedure.', '2026-10-18 23:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(424, 21, 'Complete medication instructions', 'patient_action', 'Follow the medication instructions given by the doctor before the procedure.', '2026-11-03 02:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(425, 18, 'Complete medication instructions', 'patient_action', 'Follow the medication instructions given by the doctor before the procedure.', '2026-10-22 03:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(426, 22, 'Complete medication instructions', 'patient_action', 'Follow the medication instructions given by the doctor before the procedure.', '2026-11-05 23:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(427, 23, 'Complete medication instructions', 'patient_action', 'Follow the medication instructions given by the doctor before the procedure.', '2026-11-09 21:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(428, 24, 'Complete medication instructions', 'patient_action', 'Follow the medication instructions given by the doctor before the procedure.', '2026-11-13 03:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(429, 25, 'Complete medication instructions', 'patient_action', 'Follow the medication instructions given by the doctor before the procedure.', '2026-11-16 20:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(430, 26, 'Complete medication instructions', 'patient_action', 'Follow the medication instructions given by the doctor before the procedure.', '2026-11-19 22:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(431, 27, 'Complete medication instructions', 'patient_action', 'Follow the medication instructions given by the doctor before the procedure.', '2026-11-24 01:30:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(432, 28, 'Complete medication instructions', 'patient_action', 'Follow the medication instructions given by the doctor before the procedure.', '2026-11-27 04:00:00', 1, 'pending', NULL, NULL, NULL, NULL, NULL),
(433, 9, 'Upload required medical report', 'document_upload', 'Upload the latest relevant medical report required for procedure readiness.', '2026-09-25 09:00:00', 0, 'pending', NULL, NULL, NULL, NULL, NULL),
(434, 10, 'Upload required medical report', 'document_upload', 'Upload the latest relevant medical report required for procedure readiness.', '2026-09-27 10:30:00', 0, 'pending', NULL, NULL, NULL, NULL, NULL),
(435, 11, 'Upload required medical report', 'document_upload', 'Upload the latest relevant medical report required for procedure readiness.', '2026-09-28 11:00:00', 0, 'pending', NULL, NULL, NULL, NULL, NULL),
(436, 12, 'Upload required medical report', 'document_upload', 'Upload the latest relevant medical report required for procedure readiness.', '2026-09-29 14:00:00', 0, 'pending', NULL, NULL, NULL, NULL, NULL),
(437, 13, 'Upload required medical report', 'document_upload', 'Upload the latest relevant medical report required for procedure readiness.', '2026-10-01 09:30:00', 0, 'pending', NULL, NULL, NULL, NULL, NULL),
(438, 14, 'Upload required medical report', 'document_upload', 'Upload the latest relevant medical report required for procedure readiness.', '2026-10-04 10:00:00', 0, 'pending', NULL, NULL, NULL, NULL, NULL),
(439, 15, 'Upload required medical report', 'document_upload', 'Upload the latest relevant medical report required for procedure readiness.', '2026-10-08 08:30:00', 0, 'pending', NULL, NULL, NULL, NULL, NULL),
(440, 19, 'Upload required medical report', 'document_upload', 'Upload the latest relevant medical report required for procedure readiness.', '2026-10-25 09:00:00', 0, 'pending', NULL, NULL, NULL, NULL, NULL),
(441, 16, 'Upload required medical report', 'document_upload', 'Upload the latest relevant medical report required for procedure readiness.', '2026-10-13 13:00:00', 0, 'pending', NULL, NULL, NULL, NULL, NULL),
(442, 20, 'Upload required medical report', 'document_upload', 'Upload the latest relevant medical report required for procedure readiness.', '2026-10-28 10:30:00', 0, 'pending', NULL, NULL, NULL, NULL, NULL),
(443, 17, 'Upload required medical report', 'document_upload', 'Upload the latest relevant medical report required for procedure readiness.', '2026-10-18 11:30:00', 0, 'pending', NULL, NULL, NULL, NULL, NULL),
(444, 21, 'Upload required medical report', 'document_upload', 'Upload the latest relevant medical report required for procedure readiness.', '2026-11-02 14:00:00', 0, 'pending', NULL, NULL, NULL, NULL, NULL),
(445, 18, 'Upload required medical report', 'document_upload', 'Upload the latest relevant medical report required for procedure readiness.', '2026-10-21 15:00:00', 0, 'pending', NULL, NULL, NULL, NULL, NULL),
(446, 22, 'Upload required medical report', 'document_upload', 'Upload the latest relevant medical report required for procedure readiness.', '2026-11-05 11:00:00', 0, 'pending', NULL, NULL, NULL, NULL, NULL),
(447, 23, 'Upload required medical report', 'document_upload', 'Upload the latest relevant medical report required for procedure readiness.', '2026-11-09 09:30:00', 0, 'pending', NULL, NULL, NULL, NULL, NULL),
(448, 24, 'Upload required medical report', 'document_upload', 'Upload the latest relevant medical report required for procedure readiness.', '2026-11-12 15:00:00', 0, 'pending', NULL, NULL, NULL, NULL, NULL),
(449, 25, 'Upload required medical report', 'document_upload', 'Upload the latest relevant medical report required for procedure readiness.', '2026-11-16 08:30:00', 0, 'pending', NULL, NULL, NULL, NULL, NULL),
(450, 26, 'Upload required medical report', 'document_upload', 'Upload the latest relevant medical report required for procedure readiness.', '2026-11-19 10:00:00', 0, 'pending', NULL, NULL, NULL, NULL, NULL),
(451, 27, 'Upload required medical report', 'document_upload', 'Upload the latest relevant medical report required for procedure readiness.', '2026-11-23 13:30:00', 0, 'pending', NULL, NULL, NULL, NULL, NULL),
(452, 28, 'Upload required medical report', 'document_upload', 'Upload the latest relevant medical report required for procedure readiness.', '2026-11-26 16:00:00', 0, 'pending', NULL, NULL, NULL, NULL, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_doctor_profiles`
--

CREATE TABLE `tbl_doctor_profiles` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `license_number` varchar(100) NOT NULL,
  `specialty` varchar(100) NOT NULL,
  `department` varchar(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tbl_doctor_profiles`
--

INSERT INTO `tbl_doctor_profiles` (`id`, `user_id`, `license_number`, `specialty`, `department`) VALUES
(1, 3, 'LIC-MD-99214', 'Cardiology / Electrophysiology', 'Cardiovascular Sciences'),
(2, 7, 'KL-MED-2026-001', 'Cardiology', 'Cardiology'),
(3, 8, 'KL-MED-2026-002', 'Gastroenterology', 'Gastroenterology'),
(4, 9, 'KL-MED-2026-003', 'Orthopedics', 'Orthopedics'),
(5, 10, 'KL-MED-2026-004', 'Radiology', 'Radiology');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_dynamic_checklist_templates`
--

CREATE TABLE `tbl_dynamic_checklist_templates` (
  `id` int(11) NOT NULL,
  `procedure_id` int(11) NOT NULL,
  `task_name` varchar(100) NOT NULL,
  `task_type` enum('patient_action','staff_verification','document_upload') NOT NULL,
  `description` text DEFAULT NULL,
  `due_days_before` int(11) NOT NULL DEFAULT 1,
  `is_critical` tinyint(1) NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tbl_dynamic_checklist_templates`
--

INSERT INTO `tbl_dynamic_checklist_templates` (`id`, `procedure_id`, `task_name`, `task_type`, `description`, `due_days_before`, `is_critical`) VALUES
(1, 1, 'NPO Fasting (No food or water)', 'patient_action', 'Fasting is required for at least 8 hours prior to the heart catheterization.', 1, 1),
(2, 1, 'Stop Anticoagulant (Blood Thinners)', 'patient_action', 'Temporarily suspend blood thinning medications 48 hours prior to procedure as advised by physician.', 2, 1),
(3, 1, 'Upload Recent ECG Lab Report', 'document_upload', 'Please upload a PDF or image copy of your 12-lead ECG conducted in the last 14 days.', 3, 1),
(4, 1, 'Clinical Consent Form Signature', 'patient_action', 'Verify that the physical surgical consent documentation has been signed by patient and surgeon.', 0, 1),
(5, 2, 'Liquid Prep Diet Compliance', 'patient_action', 'Complete gastroenterologist-approved colon cleansing prep formulation.', 1, 1),
(6, 2, 'Confirm Escort Driver Present', 'patient_action', 'Provide details of the responsible adult driving you home after sedation.', 0, 0);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_health_suggestions`
--

CREATE TABLE `tbl_health_suggestions` (
  `id` int(11) NOT NULL,
  `procedure_id` int(11) NOT NULL,
  `suggestion_text` text NOT NULL,
  `trigger_condition` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tbl_health_suggestions`
--

INSERT INTO `tbl_health_suggestions` (`id`, `procedure_id`, `suggestion_text`, `trigger_condition`, `created_at`) VALUES
(1, 1, 'Discontinue Metformin 48 hours prior to contrast dye exposure to prevent kidney injury.', 'diabetic', '2026-08-01 07:49:27'),
(2, 1, 'Keep your cardiac device card (Pacemaker/ICD) on your person during hospital check-in.', 'cardiac_history', '2026-08-01 07:49:27'),
(3, 2, 'Avoid eating red-colored gelatin, popsicles, or beverages 24 hours prior to colonoscopy.', 'all', '2026-08-01 07:49:27');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_notifications`
--

CREATE TABLE `tbl_notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `sender_id` int(11) DEFAULT NULL,
  `scheduled_procedure_id` int(11) DEFAULT NULL,
  `title` varchar(150) NOT NULL,
  `message` text NOT NULL,
  `type` enum('sms','email','in_app') NOT NULL DEFAULT 'in_app',
  `status` enum('unread','read','failed') NOT NULL DEFAULT 'unread',
  `sent_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tbl_notifications`
--

INSERT INTO `tbl_notifications` (`id`, `user_id`, `title`, `message`, `type`, `status`, `sent_at`) VALUES
(1, 4, 'Procedure Scheduled', 'Your Heart Catheterization has been scheduled for Aug 20, 2026 at 9:00 AM.', 'in_app', 'read', '2026-08-01 07:49:27'),
(2, 4, 'Preparation Task Alert', 'Please upload your ECG report by Aug 17, 2026.', 'sms', 'unread', '2026-08-01 07:49:27');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_patient_profiles`
--

CREATE TABLE `tbl_patient_profiles` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `date_of_birth` date NOT NULL,
  `gender` enum('male','female','other') NOT NULL,
  `blood_type` varchar(5) DEFAULT NULL,
  `medical_history` text DEFAULT NULL,
  `emergency_contact_name` varchar(100) NOT NULL,
  `emergency_contact_phone` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tbl_patient_profiles`
--

INSERT INTO `tbl_patient_profiles` (`id`, `user_id`, `date_of_birth`, `gender`, `blood_type`, `medical_history`, `emergency_contact_name`, `emergency_contact_phone`) VALUES
(1, 4, '1980-05-15', 'male', 'A+', 'Hypertension, Mild Seasonal Allergies', 'Jane Doe', '+919876543210'),
(2, 5, '1992-11-23', 'female', 'O-', 'Type-2 Diabetes', 'David Smith', '+919876543211'),
(3, 6, '1995-04-12', 'female', 'O+', 'None reported', 'Test Contact', '+919876543212'),
(4, 11, '1988-03-14', 'male', 'B+', 'No significant medical history', 'Mary Joseph', '+919876543220'),
(5, 12, '1994-07-22', 'female', 'A+', 'Mild seasonal allergies', 'Suresh Nair', '+919876543221'),
(6, 13, '1986-11-09', 'female', 'O+', 'Type-2 diabetes', 'Thomas Mathew', '+919876543222'),
(7, 14, '1991-02-18', 'male', 'AB+', 'No significant medical history', 'Anita Mathew', '+919876543223'),
(8, 15, '1997-09-30', 'female', 'O-', 'Iron deficiency anemia', 'George Thomas', '+919876543224'),
(9, 16, '1983-12-05', 'male', 'A-', 'Hypertension', 'Sunita Kumar', '+919876543225');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_patient_vitals`
--

CREATE TABLE `tbl_patient_vitals` (
  `id` int(11) NOT NULL,
  `scheduled_procedure_id` int(11) NOT NULL,
  `blood_sugar` decimal(5,2) DEFAULT NULL,
  `hemoglobin` decimal(4,2) DEFAULT NULL,
  `systolic_bp` int(11) DEFAULT NULL,
  `diastolic_bp` int(11) DEFAULT NULL,
  `temperature` decimal(4,1) DEFAULT NULL,
  `creatinine` decimal(4,2) DEFAULT NULL,
  `recorded_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tbl_patient_vitals`
--

INSERT INTO `tbl_patient_vitals` (`id`, `scheduled_procedure_id`, `blood_sugar`, `hemoglobin`, `systolic_bp`, `diastolic_bp`, `temperature`, `creatinine`, `recorded_at`) VALUES
(1, 2, 110.00, 14.00, 120, 76, 96.0, 1.00, '2026-08-09 17:16:54');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_procedures`
--

CREATE TABLE `tbl_procedures` (
  `id` int(11) NOT NULL,
  `code` varchar(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `category` varchar(50) NOT NULL,
  `est_duration_mins` int(11) NOT NULL DEFAULT 60
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tbl_procedures`
--

INSERT INTO `tbl_procedures` (`id`, `code`, `name`, `description`, `category`, `est_duration_mins`) VALUES
(1, 'CPT-93452', 'Left Heart Catheterization', 'Diagnostic assessment of blood flow and pressure within chambers of the left heart.', 'Diagnostic', 75),
(2, 'CPT-45378', 'Colonoscopy', 'Endoscopic examination of the large bowel and the distal part of the small bowel.', 'Endoscopy', 45),
(9, 'CPT-47562', 'Laparoscopic Cholecystectomy', NULL, '', 60),
(10, 'CPT-74177', 'CT Scan Abdomen and Pelvis', NULL, 'Imaging', 60),
(11, 'CPT-70553', 'MRI Brain', NULL, 'Imaging', 60),
(12, 'CPT-43239', 'Upper GI Endoscopy', NULL, 'Endoscopy', 60),
(13, 'CPT-93000', 'Electrocardiogram (ECG)', NULL, 'Diagnostic', 60);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_procedure_readiness`
--

CREATE TABLE `tbl_procedure_readiness` (
  `id` int(11) NOT NULL,
  `scheduled_procedure_id` int(11) NOT NULL,
  `readiness_status` enum('red','orange','yellow','green') NOT NULL DEFAULT 'red',
  `evaluated_by_user_id` int(11) DEFAULT NULL,
  `last_evaluated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `notes` text DEFAULT NULL,
  `override_reason` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tbl_procedure_readiness`
--

INSERT INTO `tbl_procedure_readiness` (`id`, `scheduled_procedure_id`, `readiness_status`, `evaluated_by_user_id`, `last_evaluated_at`, `notes`, `override_reason`) VALUES
(1, 1, 'red', 3, '2026-08-01 07:49:27', 'Pending patient NPO verification and clinician signature on consent form.', NULL),
(2, 2, 'orange', 3, '2026-08-09 17:17:03', 'Critical tasks completed by patient; awaiting clinician verification.', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `tbl_risk_alerts`
--

CREATE TABLE `tbl_risk_alerts` (
  `id` int(11) NOT NULL,
  `scheduled_procedure_id` int(11) NOT NULL,
  `alert_type` varchar(100) NOT NULL,
  `alert_message` text NOT NULL,
  `severity` enum('low','medium','high') NOT NULL DEFAULT 'medium',
  `is_resolved` tinyint(1) NOT NULL DEFAULT 0,
  `resolved_by_user_id` int(11) DEFAULT NULL,
  `resolved_at` datetime DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tbl_risk_alerts`
--

INSERT INTO `tbl_risk_alerts` (`id`, `scheduled_procedure_id`, `alert_type`, `alert_message`, `severity`, `is_resolved`, `resolved_by_user_id`, `resolved_at`, `created_at`) VALUES
(1, 1, 'ECG_UNVERIFIED', 'ECG document uploaded by patient but awaiting clinician validation.', 'medium', 0, NULL, NULL, '2026-08-01 07:49:27');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_roles`
--

CREATE TABLE `tbl_roles` (
  `id` int(11) NOT NULL,
  `name` varchar(50) NOT NULL,
  `description` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tbl_roles`
--

INSERT INTO `tbl_roles` (`id`, `name`, `description`) VALUES
(1, 'admin', 'System Administrator with infrastructure and template access'),
(3, 'doctor', 'Attending Surgeon performing tbl_procedures'),
(4, 'patient', 'The patient undergoing the medical procedure');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_scheduled_procedures`
--

CREATE TABLE `tbl_scheduled_procedures` (
  `id` int(11) NOT NULL,
  `patient_id` int(11) NOT NULL,
  `doctor_id` int(11) NOT NULL,
  `procedure_id` int(11) NOT NULL,
  `scheduled_at` datetime NOT NULL,
  `location` varchar(100) NOT NULL,
  `status` enum('scheduled','completed','cancelled','delayed') NOT NULL DEFAULT 'scheduled',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tbl_scheduled_procedures`
--

INSERT INTO `tbl_scheduled_procedures` (`id`, `patient_id`, `doctor_id`, `procedure_id`, `scheduled_at`, `location`, `status`, `created_at`) VALUES
(1, 4, 3, 1, '2026-09-24 09:00:00', 'Catheterization Lab 3', 'scheduled', '2026-09-24 09:00:00'),
(2, 5, 3, 2, '2026-09-25 11:30:00', 'Endoscopy Suite B', 'scheduled', '2026-09-25 11:30:00'),
(9, 15, 7, 9, '2026-09-26 09:00:00', 'Main Operation Theatre', 'scheduled', '2026-09-26 09:00:00'),
(10, 16, 8, 2, '2026-09-28 10:30:00', 'Endoscopy Unit', 'scheduled', '2026-09-28 10:30:00'),
(11, 11, 9, 10, '2026-09-29 11:00:00', 'Radiology Department', 'scheduled', '2026-09-29 11:00:00'),
(12, 12, 10, 11, '2026-09-30 14:00:00', 'MRI Center', 'scheduled', '2026-09-30 14:00:00'),
(13, 13, 7, 12, '2026-10-02 09:30:00', 'Gastroenterology Unit', 'scheduled', '2026-10-02 09:30:00'),
(14, 14, 8, 1, '2026-10-05 10:00:00', 'Cardiology Department', 'scheduled', '2026-10-05 10:00:00'),
(15, 15, 9, 13, '2026-10-09 08:30:00', 'Diagnostic Unit', 'scheduled', '2026-10-09 08:30:00'),
(16, 16, 10, 9, '2026-10-14 13:00:00', 'Main Operation Theatre', 'scheduled', '2026-10-14 13:00:00'),
(17, 11, 8, 12, '2026-10-19 11:30:00', 'Gastroenterology Unit', 'scheduled', '2026-10-19 11:30:00'),
(18, 12, 7, 10, '2026-10-22 15:00:00', 'Radiology Department', 'scheduled', '2026-10-22 15:00:00'),
(19, 11, 7, 9, '2026-10-26 09:00:00', 'Operation Theatre 1', 'scheduled', '2026-10-26 09:00:00'),
(20, 12, 8, 2, '2026-10-29 10:30:00', 'Endoscopy Suite B', 'scheduled', '2026-10-29 10:30:00'),
(21, 13, 9, 11, '2026-11-03 14:00:00', 'MRI Suite 1', 'scheduled', '2026-11-03 14:00:00'),
(22, 14, 10, 10, '2026-11-06 11:00:00', 'Radiology Department', 'scheduled', '2026-11-06 11:00:00'),
(23, 15, 7, 1, '2026-11-10 09:30:00', 'Catheterization Lab 3', 'scheduled', '2026-11-10 09:30:00'),
(24, 16, 8, 12, '2026-11-13 15:00:00', 'Endoscopy Suite A', 'scheduled', '2026-11-13 15:00:00'),
(25, 11, 9, 13, '2026-11-17 08:30:00', 'Cardiology Unit', 'completed', '2026-11-17 08:30:00'),
(26, 12, 10, 9, '2026-11-20 10:00:00', 'Operation Theatre 2', 'scheduled', '2026-11-20 10:00:00'),
(27, 13, 7, 2, '2026-11-24 13:30:00', 'Endoscopy Suite B', 'delayed', '2026-11-24 13:30:00'),
(28, 14, 8, 11, '2026-11-27 16:00:00', 'MRI Suite 2', 'scheduled', '2026-11-27 16:00:00');

-- --------------------------------------------------------

--
-- Table structure for table `tbl_uploaded_reports`
--

CREATE TABLE `tbl_uploaded_reports` (
  `id` int(11) NOT NULL,
  `checklist_item_id` int(11) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `file_path` varchar(512) NOT NULL,
  `file_size_bytes` int(11) NOT NULL,
  `uploaded_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tbl_uploaded_reports`
--

INSERT INTO `tbl_uploaded_reports` (`id`, `checklist_item_id`, `file_name`, `file_path`, `file_size_bytes`, `uploaded_at`) VALUES

-- --------------------------------------------------------

--
-- Table structure for table `tbl_users`
--

CREATE TABLE `tbl_users` (
  `id` int(11) NOT NULL,
  `role_id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `updated_at` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Dumping data for table `tbl_users`
--

INSERT INTO `tbl_users` (`id`, `role_id`, `username`, `email`, `password_hash`, `first_name`, `last_name`, `phone`, `is_active`, `created_at`, `updated_at`) VALUES
(1, 1, 'admin_clara', 'clara.admin@hospital.org', '$2b$12$sl2gMR2fmfBbCnQ7MfWsjeXwZmWiR3TpFz9uJfrRTTLFbvNTa30/y', 'Clara', 'Windsor', '+91 9876543210', 1, '2026-08-01 07:49:26', '2026-08-02 13:54:42'),
(3, 3, 'doctor_robert', 'robert.surgeon@hospital.org', '$2b$12$9WqJssy1G.HHBNstX18B1e3ldqMsID16isZ02CKY7yUzD/Sq.RJnW', 'Robert', 'Chen', '+91 9123456789', 1, '2026-08-01 07:49:26', '2026-08-02 13:54:42'),
(4, 4, 'patient_john', 'john.doe@patient.net', '$2b$12$u0UB2BxIyUDDJdk1CpKiQui2ki9Bq2KVhIGjgjI/VfwsK8ndEAHI.', 'John', 'Doe', '+91 9345678901', 1, '2026-08-01 07:49:26', '2026-08-02 13:54:42'),
(5, 4, 'patient_alice', 'alice.smith@patient.net', '$2b$12$u0UB2BxIyUDDJdk1CpKiQui2ki9Bq2KVhIGjgjI/VfwsK8ndEAHI.', 'Alice', 'Smith', '+91 9456789012', 1, '2026-08-01 07:49:26', '2026-08-02 13:54:42'),
(6, 4, 'patient_test_user', 'test.patient@hospital.org', '$2b$12$u0UB2BxIyUDDJdk1CpKiQui2ki9Bq2KVhIGjgjI/VfwsK8ndEAHI.', 'Test', 'Patient', '+91 9567890123', 1, '2026-08-02 13:48:03', '2026-08-02 13:54:42'),
(7, 3, 'doctor_anil', 'anil.kumar@hospital.org', '$2b$12$9WqJssy1G.HHBNstX18B1e3ldqMsID16isZ02CKY7yUzD/Sq.RJnW', 'Anil', 'Kumar', '+919876543210', 1, '2026-08-09 16:10:59', '2026-08-09 16:10:59'),
(8, 3, 'doctor_priya', 'priya.nair@hospital.org', '$2b$12$9WqJssy1G.HHBNstX18B1e3ldqMsID16isZ02CKY7yUzD/Sq.RJnW', 'Priya', 'Nair', '+919876543211', 1, '2026-08-09 16:10:59', '2026-08-09 16:10:59'),
(9, 3, 'doctor_rahul', 'rahul.menon@hospital.org', '$2b$12$9WqJssy1G.HHBNstX18B1e3ldqMsID16isZ02CKY7yUzD/Sq.RJnW', 'Rahul', 'Menon', '+919876543212', 1, '2026-08-09 16:10:59', '2026-08-09 16:10:59'),
(10, 3, 'doctor_sneha', 'sneha.thomas@hospital.org', '$2b$12$9WqJssy1G.HHBNstX18B1e3ldqMsID16isZ02CKY7yUzD/Sq.RJnW', 'Sneha', 'Thomas', '+919876543213', 1, '2026-08-09 16:10:59', '2026-08-09 16:10:59'),
(11, 4, 'patient_arun', 'arun.joseph@patient.net', '$2b$12$u0UB2BxIyUDDJdk1CpKiQui2ki9Bq2KVhIGjgjI/VfwsK8ndEAHI.', 'Arun', 'Joseph', '+919876543214', 1, '2026-08-09 16:10:59', '2026-08-09 16:10:59'),
(12, 4, 'patient_ananya', 'ananya.nair@patient.net', '$2b$12$u0UB2BxIyUDDJdk1CpKiQui2ki9Bq2KVhIGjgjI/VfwsK8ndEAHI.', 'Ananya', 'Nair', '+919876543215', 1, '2026-08-09 16:10:59', '2026-08-09 16:10:59'),
(13, 4, 'patient_meera', 'meera.thomas@patient.net', '$2b$12$u0UB2BxIyUDDJdk1CpKiQui2ki9Bq2KVhIGjgjI/VfwsK8ndEAHI.', 'Meera', 'Thomas', '+919876543216', 1, '2026-08-09 16:10:59', '2026-08-09 16:10:59'),
(14, 4, 'patient_rahul', 'rahul.mathew@patient.net', '$2b$12$u0UB2BxIyUDDJdk1CpKiQui2ki9Bq2KVhIGjgjI/VfwsK8ndEAHI.', 'Rahul', 'Mathew', '+919876543217', 1, '2026-08-09 16:10:59', '2026-08-09 16:10:59'),
(15, 4, 'patient_neha', 'neha.george@patient.net', '$2b$12$u0UB2BxIyUDDJdk1CpKiQui2ki9Bq2KVhIGjgjI/VfwsK8ndEAHI.', 'Neha', 'George', '+919876543218', 1, '2026-08-09 16:10:59', '2026-08-09 16:10:59'),
(16, 4, 'patient_aditya', 'aditya.kumar@patient.net', '$2b$12$u0UB2BxIyUDDJdk1CpKiQui2ki9Bq2KVhIGjgjI/VfwsK8ndEAHI.', 'Aditya', 'Kumar', '+919876543219', 1, '2026-08-09 16:10:59', '2026-08-09 16:10:59');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `tbl_checklist_items`
--
ALTER TABLE `tbl_checklist_items`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_item_sched` (`scheduled_procedure_id`),
  ADD KEY `idx_item_due` (`due_by_datetime`),
  ADD KEY `fk_item_completed_by` (`completed_by_user_id`),
  ADD KEY `fk_item_verified_by` (`verified_by_user_id`);

--
-- Indexes for table `tbl_doctor_profiles`
--
ALTER TABLE `tbl_doctor_profiles`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_doc_user` (`user_id`),
  ADD UNIQUE KEY `uq_doc_license` (`license_number`);

--
-- Indexes for table `tbl_dynamic_checklist_templates`
--
ALTER TABLE `tbl_dynamic_checklist_templates`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_template_proc` (`procedure_id`);

--
-- Indexes for table `tbl_health_suggestions`
--
ALTER TABLE `tbl_health_suggestions`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_sugg_proc` (`procedure_id`);

--
-- Indexes for table `tbl_notifications`
--
ALTER TABLE `tbl_notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_notif_user` (`user_id`),
  ADD KEY `idx_notif_status` (`status`);

--
-- Indexes for table `tbl_patient_profiles`
--
ALTER TABLE `tbl_patient_profiles`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_pat_user` (`user_id`);

--
-- Indexes for table `tbl_patient_vitals`
--
ALTER TABLE `tbl_patient_vitals`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_vitals_sched` (`scheduled_procedure_id`);

--
-- Indexes for table `tbl_procedures`
--
ALTER TABLE `tbl_procedures`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_proc_code` (`code`),
  ADD KEY `idx_proc_name` (`name`);

--
-- Indexes for table `tbl_procedure_readiness`
--
ALTER TABLE `tbl_procedure_readiness`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_readiness_sched` (`scheduled_procedure_id`),
  ADD KEY `fk_readiness_eval_by` (`evaluated_by_user_id`);

--
-- Indexes for table `tbl_risk_alerts`
--
ALTER TABLE `tbl_risk_alerts`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_alert_sched` (`scheduled_procedure_id`),
  ADD KEY `idx_alert_resolved` (`is_resolved`),
  ADD KEY `fk_alert_resolved_by` (`resolved_by_user_id`);

--
-- Indexes for table `tbl_roles`
--
ALTER TABLE `tbl_roles`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_role_name` (`name`);

--
-- Indexes for table `tbl_scheduled_procedures`
--
ALTER TABLE `tbl_scheduled_procedures`
  ADD PRIMARY KEY (`id`),
  ADD KEY `idx_sched_time` (`scheduled_at`),
  ADD KEY `idx_sched_patient` (`patient_id`),
  ADD KEY `idx_sched_doctor` (`doctor_id`),
  ADD KEY `fk_sched_proc` (`procedure_id`);

--
-- Indexes for table `tbl_uploaded_reports`
--
ALTER TABLE `tbl_uploaded_reports`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_report_item` (`checklist_item_id`);

--
-- Indexes for table `tbl_users`
--
ALTER TABLE `tbl_users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uq_username` (`username`),
  ADD UNIQUE KEY `uq_email` (`email`),
  ADD KEY `idx_user_role` (`role_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `tbl_checklist_items`
--
ALTER TABLE `tbl_checklist_items`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=480;

--
-- AUTO_INCREMENT for table `tbl_doctor_profiles`
--
ALTER TABLE `tbl_doctor_profiles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- AUTO_INCREMENT for table `tbl_dynamic_checklist_templates`
--
ALTER TABLE `tbl_dynamic_checklist_templates`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `tbl_health_suggestions`
--
ALTER TABLE `tbl_health_suggestions`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `tbl_notifications`
--
ALTER TABLE `tbl_notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `tbl_patient_profiles`
--
ALTER TABLE `tbl_patient_profiles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT for table `tbl_patient_vitals`
--
ALTER TABLE `tbl_patient_vitals`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `tbl_procedures`
--
ALTER TABLE `tbl_procedures`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=14;

--
-- AUTO_INCREMENT for table `tbl_procedure_readiness`
--
ALTER TABLE `tbl_procedure_readiness`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `tbl_risk_alerts`
--
ALTER TABLE `tbl_risk_alerts`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `tbl_roles`
--
ALTER TABLE `tbl_roles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT for table `tbl_scheduled_procedures`
--
ALTER TABLE `tbl_scheduled_procedures`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- AUTO_INCREMENT for table `tbl_uploaded_reports`
--
ALTER TABLE `tbl_uploaded_reports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `tbl_users`
--
ALTER TABLE `tbl_users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `tbl_checklist_items`
--
ALTER TABLE `tbl_checklist_items`
  ADD CONSTRAINT `fk_item_completed_by` FOREIGN KEY (`completed_by_user_id`) REFERENCES `tbl_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_item_sched` FOREIGN KEY (`scheduled_procedure_id`) REFERENCES `tbl_scheduled_procedures` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_item_verified_by` FOREIGN KEY (`verified_by_user_id`) REFERENCES `tbl_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE;

--
-- Constraints for table `tbl_doctor_profiles`
--
ALTER TABLE `tbl_doctor_profiles`
  ADD CONSTRAINT `fk_doc_user` FOREIGN KEY (`user_id`) REFERENCES `tbl_users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `tbl_dynamic_checklist_templates`
--
ALTER TABLE `tbl_dynamic_checklist_templates`
  ADD CONSTRAINT `fk_template_proc` FOREIGN KEY (`procedure_id`) REFERENCES `tbl_procedures` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `tbl_health_suggestions`
--
ALTER TABLE `tbl_health_suggestions`
  ADD CONSTRAINT `fk_sugg_proc` FOREIGN KEY (`procedure_id`) REFERENCES `tbl_procedures` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `tbl_notifications`
--
ALTER TABLE `tbl_notifications`
  ADD CONSTRAINT `fk_notif_user` FOREIGN KEY (`user_id`) REFERENCES `tbl_users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_notif_sender` FOREIGN KEY (`sender_id`) REFERENCES `tbl_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_notif_procedure` FOREIGN KEY (`scheduled_procedure_id`) REFERENCES `tbl_scheduled_procedures` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `tbl_patient_profiles`
--
ALTER TABLE `tbl_patient_profiles`
  ADD CONSTRAINT `fk_pat_user` FOREIGN KEY (`user_id`) REFERENCES `tbl_users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `tbl_patient_vitals`
--
ALTER TABLE `tbl_patient_vitals`
  ADD CONSTRAINT `fk_vitals_sched` FOREIGN KEY (`scheduled_procedure_id`) REFERENCES `tbl_scheduled_procedures` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `tbl_procedure_readiness`
--
ALTER TABLE `tbl_procedure_readiness`
  ADD CONSTRAINT `fk_readiness_eval_by` FOREIGN KEY (`evaluated_by_user_id`) REFERENCES `tbl_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_readiness_sched` FOREIGN KEY (`scheduled_procedure_id`) REFERENCES `tbl_scheduled_procedures` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `tbl_risk_alerts`
--
ALTER TABLE `tbl_risk_alerts`
  ADD CONSTRAINT `fk_alert_resolved_by` FOREIGN KEY (`resolved_by_user_id`) REFERENCES `tbl_users` (`id`) ON DELETE SET NULL ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_alert_sched` FOREIGN KEY (`scheduled_procedure_id`) REFERENCES `tbl_scheduled_procedures` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `tbl_scheduled_procedures`
--
ALTER TABLE `tbl_scheduled_procedures`
  ADD CONSTRAINT `fk_sched_doctor` FOREIGN KEY (`doctor_id`) REFERENCES `tbl_users` (`id`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_sched_patient` FOREIGN KEY (`patient_id`) REFERENCES `tbl_users` (`id`) ON UPDATE CASCADE,
  ADD CONSTRAINT `fk_sched_proc` FOREIGN KEY (`procedure_id`) REFERENCES `tbl_procedures` (`id`) ON UPDATE CASCADE;

--
-- Constraints for table `tbl_uploaded_reports`
--
ALTER TABLE `tbl_uploaded_reports`
  ADD CONSTRAINT `fk_report_item` FOREIGN KEY (`checklist_item_id`) REFERENCES `tbl_checklist_items` (`id`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `tbl_users`
--
ALTER TABLE `tbl_users`
  ADD CONSTRAINT `fk_users_role` FOREIGN KEY (`role_id`) REFERENCES `tbl_roles` (`id`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
