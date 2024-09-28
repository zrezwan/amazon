#include <string>
#include "clothing.h"
#include "util.h"
#include "product.h"

using namespace std;

Clothing::Clothing(const std::string name, double price, int qty, string size, string brand) :
    Product("clothing", name, price, qty),
    size_(size),
    brand_(brand) 
{}

std::set<std::string> Clothing::keywords() const {
    set<string> ret = parseStringToWords(convToLower(name_));
    set<string> brandKeywords = parseStringToWords(convToLower(brand_));
    ret.insert(brandKeywords.begin(), brandKeywords.end());
    return ret;
}

string Clothing::displayString() const {
    return name_ + "\nSize: " + size_ + " Brand: " + brand_ + "\n" + to_string(price_) + " " + to_string(qty_) + " left." ;
}

void Clothing::dump(std::ostream& os) const {
    os << "clothing\n" << name_ << "\n" << price_ << "\n" << qty_ << "\n" << size_ << "\n" << brand_ << endl;
}