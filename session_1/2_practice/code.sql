-- Enable readable output format
.mode columns
.headers on

-- Instructions for students:
-- 1. Open SQLite in terminal: sqlite3 library.db
-- 2. Load this script: .read code.sql
-- 3. Exit SQLite: .exit


-- 1. List all loans - Show book title, member name, and loan date
SELECT Books.title, Members.name, Loans.loan_date
FROM Loans
JOIN Books ON Loans.book_id = Books.id
JOIN Members ON Loans.member_id = Members.id;

-- 2. Books and loans - List all books and any loans associated with them
SELECT Books.title, Loans.loan_date, Loans.return_date
FROM Books
LEFT JOIN Loans ON Books.id = Loans.book_id;

-- 3. Branches and books - List all library branches and the books they hold
SELECT Branches.name AS branch_name, Books.title
FROM Branches
LEFT JOIN Books ON Branches.id = Books.branch_id;

-- 4. Branch book counts - Show each library branch and the number of books it holds
SELECT Branches.name AS branch_name, COUNT(Books.id) AS book_count
FROM Branches
LEFT JOIN Books ON Branches.id = Books.branch_id
GROUP BY Branches.id;

-- 5. Branches with more than 7 books
SELECT Branches.name AS branch_name, COUNT(Books.id) AS book_count
FROM Branches
LEFT JOIN Books ON Branches.id = Books.branch_id
GROUP BY Branches.id
HAVING COUNT(Books.id) > 7;

-- 6. Members and loans - List all members and the number of loans they have made
SELECT Members.name, COUNT(Loans.id) AS loan_count
FROM Members
LEFT JOIN Loans ON Members.id = Loans.member_id
GROUP BY Members.id;

-- 7. Members who never borrowed - Identify members who have never borrowed a book
SELECT Members.name
FROM Members
LEFT JOIN Loans ON Members.id = Loans.member_id
WHERE Loans.id IS NULL;

-- 8. Branch loan totals - For each library branch, show the total number of loans for books in that branch
SELECT Branches.name AS branch_name, COUNT(Loans.id) AS total_loans
FROM Branches
LEFT JOIN Books ON Branches.id = Books.branch_id
LEFT JOIN Loans ON Books.id = Loans.book_id
GROUP BY Branches.id;

-- 9. Members with active loans - List members who currently have at least one active loan
SELECT DISTINCT Members.name
FROM Members
JOIN Loans ON Members.id = Loans.member_id
WHERE Loans.return_date IS NULL OR Loans.return_date > DATE('now');

-- 10. Books and loans report - Show all books and all loans, including books that were never loaned
-- Include a column classifying each row as "Loaned book" or "Unloaned book"
SELECT Books.title, Loans.loan_date, Loans.return_date,
    CASE 
        WHEN Loans.id IS NOT NULL THEN 'Loaned book'
        ELSE 'Unloaned book'
    END AS status
FROM Books
LEFT JOIN Loans ON Books.id = Loans.book_id;
