#include <string>
#include <iomanip>
#include "book.h"
#include "util.h"
#include "product.h"

using namespace std;

Book::Book(const std::string name, double price, int qty, string isbn, string author) :
    Product("book", name, price, qty),
    isbn_(isbn),
    author_(author) 
{}

std::set<std::string> Book::keywords() const {
    set<string> ret = parseStringToWords(convToLower(name_));
    set<string> authorKeywords = parseStringToWords(convToLower(author_));
    ret.insert(authorKeywords.begin(), authorKeywords.end());
    ret.insert(isbn_);
    return ret;
}

string Book::displayString() const {
    return name_ + "\nAuthor: " + author_ + " ISBN: " + isbn_ + "\n" + to_string(price_) + " " + to_string(qty_) + " left." ;
}

void Book::dump(std::ostream& os) const {
    os << "book\n" << name_ << "\n" << setprecision(2) << price_ << "\n" << qty_ << "\n" << isbn_ << "\n" << author_ << endl;
}