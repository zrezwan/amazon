#include <string>
#include <set>
#include <map>
#include <list>
#include <vector>
#include "product.h"
#include "user.h"
#include "mydatastore.h"
#include "util.h"

using namespace std;
MyDataStore::~MyDataStore() {
    for (map<string, User*>::iterator it = users.begin(); it != users.end(); ++it) {
        delete it->second;
    }
    for (size_t i= 0; i < products.size(); i++) {
        delete products[i];
    }
}
/**
 * Adds a product to the data store
 */
void MyDataStore::addProduct(Product* p) {
    products.push_back(p);

    // Adds this product to mapping between search keywords and products
    set<string> keys = p->keywords();
    for (set<string>::iterator it = keys.begin(); it != keys.end(); ++it) {
        mapping[*it].insert(p);
    }
}

/**
 * Adds a user to the data store
 */
void MyDataStore::addUser(User* u) {
    users.insert(make_pair(u->getName(), u));
}

/**
 * Performs a search of products whose keywords match the given "terms"
 *  type 0 = AND search (intersection of results for each term) while
 *  type 1 = OR search (union of results for each term)
 */
std::vector<Product*> MyDataStore::search(std::vector<std::string>& terms, int type) {
    set<Product *> returnSet;
    vector<Product *> ret;
    map<string, set<Product *>>::iterator it;
    if (!type) {
        it = mapping.find(terms[0]);
        // If a keyword in AND search has no results, return empty results list
        if (it == mapping.end()) {
            return ret;
        } 
        // Adds the first keyword to return list as otherwise every intersection with empty list will be empty
        else {
            returnSet = it->second;
        }
        for (size_t i = 1; i < terms.size(); i++) {
            it = mapping.find(terms[i]);
            if (it == mapping.end()) {
                return ret;
            } 
            // Updates return list to have items present in return list so far and this search
            else {
                returnSet = setIntersection(returnSet, it->second);
            }
        }
    } else {
        for (size_t i = 0; i < terms.size(); i++) {
            it = mapping.find(terms[i]);
            if (it != mapping.end()) {
                returnSet = setUnion(returnSet, it->second);
            }
        }
    }
    // Converts set to vector
    for (set<Product *>::iterator it = returnSet.begin(); it != returnSet.end(); ++it) {
        ret.push_back(*it);
    }
    return ret;
}

/**
 * Reproduce the database file from the current Products and User values
 */
void MyDataStore::dump(std::ostream& ofile) {
    ofile << "<products>" << endl;
    for (Product * p : products) {
        p->dump(ofile);
    }
    ofile << "</products>\n<users>" << endl;
    for (map<string, User *>::iterator it = users.begin(); it != users.end(); ++it) {
        it->second->dump(ofile);
    }
    ofile << "</users>" << endl;
}

// Returns true for errors present
bool MyDataStore::addToCart(std::string username, Product * product) {
    std::map<std::string, User *>::iterator userIt = users.find(username);
    // Invalid username
    if (userIt == users.end())
    {
        return true;
    }
    carts[username].push_back(product);
    return false;
}

// Returns true for errors present
bool MyDataStore::viewCart(string username) {
    std::map<std::string, User *>::iterator userIt = users.find(username);
    // Invalid username
    if (userIt == users.end())
    {
        return true;
    }

    // User's cart
    list<Product *> cart = carts[username];

    cout << endl;
    int i = 1;
    for (list<Product *>::iterator prodIt = cart.begin(); prodIt != cart.end(); ++prodIt) {
        cout << "Item " << i++ << endl;
        cout << (*prodIt)->displayString() << endl;
    }
    return false;
}

// Returns true for errors present
bool MyDataStore::buyCart(string username) {
    std::map<std::string, User *>::iterator userIt = users.find(username);
    // Invalid username
    if (userIt == users.end())
    {
        return true;
    }

    // User's cart
    list<Product *> cart = carts[username];

    for (list<Product *>::iterator prodIt = cart.begin(); prodIt != cart.end();) {
        // Reduces quantity of product, balance of user, and item in cart if user can buy with balance 
        if ( (*prodIt)->getQty() && userIt->second->getBalance() >= (*prodIt)->getPrice() ) {
            (*prodIt)->subtractQty(1);
            userIt->second->deductAmount((*prodIt)->getPrice());
            prodIt = cart.erase(prodIt);
            // erase returns next iterator so need to update iterator
            continue;
        }
        // Updates iterator to go to next item if could not purchase this item 
        ++prodIt;
    }
    // Updates user's cart in data member
    carts[username] = cart;
    return false;
}