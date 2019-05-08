-- This file includes queries for changing the character set for the database and some existing table.
-- The reason for this was to be able to include emojis. 

ALTER DATABASE `nettside` CHARACTER SET = utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE content_category CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE content_jobpost CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE content_news CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE content_event CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE content_warning CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE django_admin_log CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;