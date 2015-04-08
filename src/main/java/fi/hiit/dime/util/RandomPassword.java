/*
  Copyright (c) 2015 University of Helsinki

  Permission is hereby granted, free of charge, to any person
  obtaining a copy of this software and associated documentation files
  (the "Software"), to deal in the Software without restriction,
  including without limitation the rights to use, copy, modify, merge,
  publish, distribute, sublicense, and/or sell copies of the Software,
  and to permit persons to whom the Software is furnished to do so,
  subject to the following conditions:

  The above copyright notice and this permission notice shall be
  included in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
  BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
  ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
  CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
  SOFTWARE.
*/

package fi.hiit.dime.util;

//------------------------------------------------------------------------------

import java.security.SecureRandom;

//------------------------------------------------------------------------------

public class RandomPassword {
    private SecureRandom mRand;

    private final static String chars_alpha =
	"abcdefghijklmnopqrstuvwxyz" +
	"ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    
    private final static String chars_numeric = 
	"01234567890";

    private final static String chars_symbols = 
	"_,.;:!#%&/()={}[]?+^<>*";
    
    public RandomPassword() {
	mRand = new SecureRandom();
	// FIXME: implement handling of seed
    }

    public String getPassword(int length, boolean numeric, boolean symbols) {
	StringBuilder chars = new StringBuilder(chars_alpha);
	if (numeric)
	    chars.append(chars_numeric);
	if (symbols)
	    chars.append(chars_symbols);

	StringBuilder p = new StringBuilder(length);
	int l = chars.length();
	
	for (int i=0; i<length;) {
	    byte b[] = new byte[1];
	    mRand.nextBytes(b);
	    int r = b[0] & 0xff;
	    if (r < l) {
		p.append(chars.charAt(r));
		i++;
	    }
	}
	return p.toString();
    }

    public String getPassword(int length) {
	return getPassword(length, true, true);
    }
}
