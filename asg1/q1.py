records = [
    ("Mon",["Python","Java","Python"]),
    ("Tue",["C++","Python"]),
    ("Wed",["Java","C++","C++","Python"]),
    ("Thu",[]),
    ("Fri",["Python","Java"])
]

def library_report(records):
    # 1 & 2. Skip days with no books borrowed and combine all borrowed books into single list
    all_books=[]
    for day,books in records:
        if books:
            all_books.extend(books)
    print(f'q1: {all_books}')
    print("\n")

    # 3. Count how many times each book was borrowed using a dictionary
    book_count={}
    for book in all_books:
        if book in book_count:
            book_count[book]+=1
        else:
            book_count[book]=1

    print(f'q2 {book_count}')
    print("\n")

    # 4. Create a set of unique book names
    unique_books=set(all_books)
    print(f'q4 {unique_books}')
    print("\n")

    # 5. Using control flow, find the most and least borrowed books
    most_borrowed=None
    least_borrowed=None

    max_count=float('-inf')
    min_count=float('inf')

    for book in book_count:
        count=book_count[book]

        if count>max_count:
            max_count=count
            most_borrowed=book

        if count<min_count:
            min_count=count
            least_borrowed=book
    print(f'q5 {most_borrowed}')
    print(least_borrowed)
    print("\n")

    # 6. Using a dictionary comprehension, create a new dictionary where 
    # books borrowed more than 2 times are labeled as "Popular".

    popular_books={book:"Popular" for book in book_count if book_count[book]>2}
    print(f'q6 {popular_books}')
    print("\n")

    '''
    7. Return a neatly formatted summary string displaying:
        a. Each book with its borrow count
        b. The most borrowed book
        c. The least borrowed book
    '''
    final="Library Report\n"

    for book,count in book_count.items():
        final+=f"{book}:{count}\n"

    final+=f"\nMost Borrowed Book:{most_borrowed}\n"
    final+=f"Least Borrowed Book:{least_borrowed}"

    print(f'q7 {final}')

library_report(records)

