package fi.hiit.dime;

//import org.springframework.security.config.annotation.web.servlet.configuration.EnableWebMvcSecurity;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.autoconfigure.security.SecurityProperties;
import org.springframework.boot.autoconfigure.security.SecurityProperties;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.annotation.Order;
import org.springframework.security.config.annotation.authentication.builders.AuthenticationManagerBuilder;
import org.springframework.security.config.annotation.method.configuration.EnableGlobalMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.WebSecurityConfigurerAdapter;
import org.springframework.security.core.userdetails.UserDetailsService;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;

//@EnableGlobalMethodSecurity(prePostEnabled = true)

@Configuration
@Order(SecurityProperties.ACCESS_OVERRIDE_ORDER)
public class WebSecurityConfig extends WebSecurityConfigurerAdapter {

    @Autowired
    private UserDetailsService userDetailsService;

    @Override
    protected void configure(HttpSecurity http) throws Exception {
        http.authorizeRequests()
	    .antMatchers("/", "/css/*", "/js/*", "/user/**", "/users/**").permitAll()
	    .anyRequest().fullyAuthenticated()
	    .and()
	    // login
            .formLogin()
	    .loginPage("/login")
	    .failureUrl("/login?error")
	    .usernameParameter("username")
	    .permitAll()
	    .and()
	    // logout
            .logout()
	    .logoutUrl("/logout")
	    .deleteCookies("remember-me")
	    .logoutSuccessUrl("/")
	    .permitAll()
	    .and()
	    .rememberMe();
    }

    @Override
    protected void configure(AuthenticationManagerBuilder auth) throws Exception {
    	auth.userDetailsService(userDetailsService)
	    .passwordEncoder(new BCryptPasswordEncoder());
    }

    // @Autowired
    // public void configureGlobal(AuthenticationManagerBuilder auth) throws Exception {
    //     auth
    //         .inMemoryAuthentication()
    //             .withUser("user").password("password").roles("USER");
    // }
}
