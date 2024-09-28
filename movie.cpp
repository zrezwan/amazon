#include <string>
#include "util.h"
#include "product.h"
#include "movie.h"

using namespace std;

Movie::Movie(const std::string name, double price, int qty, string genre, string rating) :
    Product("movie", name, price, qty),
    genre_(genre),
    rating_(rating) 
{}

std::set<std::string> Movie::keywords() const {
    set<string> ret = parseStringToWords(convToLower(name_));
    set<string> genreKeywords = parseStringToWords(convToLower(genre_));
    ret.insert(genreKeywords.begin(), genreKeywords.end());
    return ret;
}

string Movie::displayString() const {
    return name_ + "\nGenre: " + genre_ + " Rating: " + rating_ + "\n" + to_string(price_) + " " + to_string(qty_) + " left." ;
}

void Movie::dump(std::ostream& os) const {
    os << "movie\n" << name_ << "\n" << price_ << "\n" << qty_ << "\n" << genre_ << "\n" << rating_ << endl;
}