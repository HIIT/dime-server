package fi.hiit.dime;

import java.util.List;

import org.springframework.data.mongodb.repository.MongoRepository;

public interface ZeitgeistEventRepository extends MongoRepository<ZeitgeistEvent, String> {

    public List<ZeitgeistEvent> findByActor(String actor);
}
