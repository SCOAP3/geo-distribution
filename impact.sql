SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

DROP SCHEMA IF EXISTS `impact` ;
CREATE SCHEMA IF NOT EXISTS `impact` DEFAULT CHARACTER SET latin1 ;
USE `impact` ;

-- -----------------------------------------------------
-- Table `impact`.`country`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `impact`.`country` ;

CREATE TABLE IF NOT EXISTS `impact`.`country` (
  `idcountry` INT(11) NOT NULL AUTO_INCREMENT,
  `country_name` VARCHAR(60) NOT NULL,
  `gdp` INT(11) NOT NULL,
  `scientific_output` VARCHAR(45) NOT NULL,
  `code` VARCHAR(2) NULL DEFAULT NULL,
  `rank1` INT(11) NULL DEFAULT NULL,
  `rank2` INT(11) NULL DEFAULT NULL COMMENT 'based on ranking 1',
  `rank3` INT(11) NULL DEFAULT NULL COMMENT 'GDP PPP',
  `rank4` INT(11) NULL DEFAULT NULL COMMENT 'RCA 1/2 + GDP 1/2',
  PRIMARY KEY (`idcountry`),
  UNIQUE INDEX `country_name_UNIQUE` (`country_name` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 204
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `impact`.`affiliation`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `impact`.`affiliation` ;

CREATE TABLE IF NOT EXISTS `impact`.`affiliation` (
  `idaffiliation` INT(11) NOT NULL AUTO_INCREMENT,
  `aff_name` VARCHAR(400) NOT NULL,
  `idcountry` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`idaffiliation`),
  INDEX `aaa_idx` (`idcountry` ASC),
  CONSTRAINT `affiliation_country`
    FOREIGN KEY (`idcountry`)
    REFERENCES `impact`.`country` (`idcountry`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 17422
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `impact`.`author`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `impact`.`author` ;

CREATE TABLE IF NOT EXISTS `impact`.`author` (
  `idauthor` INT(11) NOT NULL AUTO_INCREMENT,
  `author_name` VARCHAR(200) NOT NULL,
  `orcid` VARCHAR(45) NULL DEFAULT NULL,
  `co_author` TINYINT(1) NOT NULL,
  PRIMARY KEY (`idauthor`))
ENGINE = InnoDB
AUTO_INCREMENT = 629651
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `impact`.`auth_affiliation`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `impact`.`auth_affiliation` ;

CREATE TABLE IF NOT EXISTS `impact`.`auth_affiliation` (
  `idauthor` INT(11) NULL DEFAULT NULL,
  `idaffiliation` INT(11) NULL DEFAULT NULL,
  INDEX `aaa_idx` (`idauthor` ASC),
  INDEX `bbb_idx` (`idaffiliation` ASC),
  CONSTRAINT `author_affilaiotion_aff`
    FOREIGN KEY (`idaffiliation`)
    REFERENCES `impact`.`affiliation` (`idaffiliation`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `author_affiliation`
    FOREIGN KEY (`idauthor`)
    REFERENCES `impact`.`author` (`idauthor`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `impact`.`record`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `impact`.`record` ;

CREATE TABLE IF NOT EXISTS `impact`.`record` (
  `idrecord` INT(11) NOT NULL,
  `journal_name` VARCHAR(45) NOT NULL,
  `publisher` VARCHAR(45) NOT NULL,
  `pub_year` INT(11) NOT NULL,
  PRIMARY KEY (`idrecord`),
  UNIQUE INDEX `idrecord_UNIQUE` (`idrecord` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `impact`.`rec_author`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `impact`.`rec_author` ;

CREATE TABLE IF NOT EXISTS `impact`.`rec_author` (
  `idrecord` INT(11) NULL DEFAULT NULL,
  `idauthor` INT(11) NULL DEFAULT NULL,
  INDEX `aaa_idx` (`idrecord` ASC),
  INDEX `bbb_idx` (`idauthor` ASC),
  CONSTRAINT `record_author_auth`
    FOREIGN KEY (`idauthor`)
    REFERENCES `impact`.`author` (`idauthor`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `record_author_rec`
    FOREIGN KEY (`idrecord`)
    REFERENCES `impact`.`record` (`idrecord`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
