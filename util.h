#ifndef UTIL_H
#define UTIL_H

#include <string>
#include <iostream>
#include <set>


/** Complete the setIntersection and setUnion functions below
 *  in this header file (since they are templates).
 *  Both functions should run in time O(n*log(n)) and not O(n^2)
 */
template <typename T>
std::set<T> setIntersection(std::set<T>& s1, std::set<T>& s2)
{
    std::set<T> ret; 
    for(typename std::set<T>::iterator it= s2.begin(); it != s2.end(); ++it)  {
        // If item in both s1 and s2, adds to return set
        if (s1.find(*it) != s1.end()) {
            ret.insert(*it);
        }
    }
    return ret;
}
template <typename T>
std::set<T> setUnion(std::set<T>& s1, std::set<T>& s2)
{
    std::set<T> ret = s1;
    for(typename std::set<T>::iterator it= s2.begin(); it != s2.end(); ++it)
    {
        // Will add item to return set if not already present; it will do nothing if present
        ret.insert(*it);
    }
    return ret;
}

/***********************************************/
/* Prototypes of functions defined in util.cpp */
/***********************************************/

std::string convToLower(std::string src);

std::set<std::string> parseStringToWords(std::string line);

// Used from http://stackoverflow.com/questions/216823/whats-the-best-way-to-trim-stdstring
// Removes any leading whitespace
std::string &ltrim(std::string &s) ;

// Removes any trailing whitespace
std::string &rtrim(std::string &s) ;

// Removes leading and trailing whitespace
std::string &trim(std::string &s) ;
#endif
