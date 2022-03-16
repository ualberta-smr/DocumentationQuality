CREATE TABLE tasks (
    id INT NOT NULL AUTO_INCREMENT,
    library_name VARCHAR(50) NOT NULL,
    paragraph VARCHAR(500) NOT NULL,
    task VARCHAR(100) NOT NULL,
    has_example BOOLEAN,
    PRIMARY KEY (id)
)