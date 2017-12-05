/*
  Copyright (c) 2015-2017 University of Helsinki

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

import static org.junit.Assert.*;
import org.junit.Before;
import org.junit.Test;

//------------------------------------------------------------------------------

public class RandomPasswordTest {
    private RandomPassword rand;

    @Before
    public void setup() {
        rand = new RandomPassword();
    }

    @Test
    public void testLength() {
        for (int i=1; i<30; i++) {
            String p1 = rand.getPassword(i, true, true);
            String p2 = rand.getPassword(i, false, true);
            String p3 = rand.getPassword(i, true, false);
            String p4 = rand.getPassword(i, false, false);

            System.out.println("p1 = " + p1);
            System.out.println("p2 = " + p2);
            System.out.println("p3 = " + p3);
            System.out.println("p4 = " + p4);

            assertEquals(p1.length(), i);
            assertEquals(p2.length(), i);
            assertEquals(p3.length(), i);
            assertEquals(p4.length(), i);
        }
    }

    //FIXME: test contents
}
