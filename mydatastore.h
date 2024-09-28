#include <string>
#include <set>
#include <map>
#include <list>
#include <deque>
#include <vector>
#include "product.h"
#include "user.h"
#include "datastore.h"

class MyDataStore : public DataStore {
    public:
        MyDataStore() {}
        ~MyDataStore();
        /**
         * Adds a product to the data store
         */
        virtual void addProduct(Product* p);

        /**
         * Adds a user to the data store
         */
        virtual void addUser(User* u);

        /**
         * Performs a search of products whose keywords match the given "terms"
         *  type 0 = AND search (intersection of results for each term) while
         *  type 1 = OR search (union of results for each term)
         */
        virtual std::vector<Product*> search(std::vector<std::string>& terms, int type);

        /**
         * Reproduce the database file from the current Products and User values
         */
        virtual void dump(std::ostream& ofile);

        // Adds product to username's cart
        bool addToCart(std::string username, Product * product);

        // Prints out items in username's cart
        bool viewCart(std::string username);

        // Buys the items in username's cart to subtract product quantity and username's balance
        bool buyCart(std::string username);
    private:
        std::map<std::string, std::set<Product *>> mapping;
        std::vector<Product* > products;
        std::map<std::string, User *> users;
        std::map<std::string, std::list<Product*>> carts;
};