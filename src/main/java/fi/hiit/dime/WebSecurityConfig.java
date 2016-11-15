/*
  Copyright (c) 2015-2016 University of Helsinki

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

package fi.hiit.dime;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.annotation.Order;
import org.springframework.http.HttpMethod;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

@EnableWebSecurity
public class WebSecurityConfig {
    @Autowired
    private UserDetailsService userDetailsService;

    @Autowired
    protected void configureGlobal(AuthenticationManagerBuilder auth) 
        throws Exception 
    {
    	auth.userDetailsService(userDetailsService)
	    .passwordEncoder(new BCryptPasswordEncoder());
    }


    @Configuration
    // @Order(1)
    public static class ApiWebSecurityConfigurationAdapter 
        extends WebSecurityConfigurerAdapter 
    {
        @Override
        protected void configure(HttpSecurity http) throws Exception {
            http.antMatcher("/api/**") 
                .authorizeRequests()
                .antMatchers("/api/ping").permitAll()
                .antMatchers(HttpMethod.POST, "/api/users").permitAll()
                .antMatchers(HttpMethod.OPTIONS, "/api/**").permitAll()
                .anyRequest().fullyAuthenticated()
                .and()
                .httpBasic()
                .and()
                .csrf().disable();
        }
    }

    // @Configuration
    // public static class FormLoginWebSecurityConfigurerAdapter 
    //     extends WebSecurityConfigurerAdapter 
    // {
    //     @Override
    //     protected void configure(HttpSecurity http) throws Exception {
    //         http.antMatcher("/**").anyRequest().permitAll();
    //         // http.authorizeRequests()
    //         //     .antMatchers("/", "/css/*", "/js/*", "/user/create",
    //         //                  "/favicon.*").permitAll()
    //         //     .antMatchers("/users/**").hasAuthority("ADMIN")
    //         //     .anyRequest().fullyAuthenticated()
    //         //     .and()
    //         //     //
    //         //     .exceptionHandling()
    //         //     .accessDeniedPage("/login?accessdenied") //OR 
    //         //     .and()
    //         //     .formLogin()
    //         //     .loginPage("/login")
    //         //     .failureUrl("/login?error")
    //         //     .usernameParameter("username")
    //         //     .permitAll()
    //         //     .and()
    //         //     // logout
    //         //     .logout()
    //         //     .logoutUrl("/logout")
    //         //     .deleteCookies("remember-me")
    //         //     .logoutSuccessUrl("/")
    //         //     .permitAll()
    //         //     .and()
    //         //     // remember me
    //         //     .rememberMe();
    //     }
    // }
}
