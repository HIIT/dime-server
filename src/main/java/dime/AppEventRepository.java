package dime;

import java.util.List;

import org.springframework.data.mongodb.repository.MongoRepository;

public interface AppEventRepository extends MongoRepository<AppEvent, String> {

    public List<AppEvent> findByName(String name);
}
