
import random
import numpy as np
import math

class Person:
    """The person class stores information about a person in the sim."""
    counter = 1
    def __init__ (self, mother, father, birthYear, age, sex, house, sec, cr, pcr, wage, inc, wlt, iw, fw, we, status, independence):
        self.mother = mother
        self.motherID = -1 # For pickle
        self.father = father
        self.fatherID = -1 # For pickle
        self.age = age
        self.status = status
        self.lifeExpectancy = 0
        self.independentStatus = independence
        self.maternityStatus = False
        self.children = []
        self.childrenID = [] # For pickle
        self.yearMarried = []
        self.yearDivorced = []
        self.deadYear = 0
        self.yearInTown = 0
        self.outOfTownStudent = False
        self.birthdate = birthYear
        self.wage = wage
        self.income = inc
        self.workingPeriods = 0
        self.cumulativeIncome = 0
        self.potentialIncome = inc
        self.wealth = wlt
        self.financialWealth = 0
        self.wealthPV = 0
        self.wealthForCare = 0
        self.initialIncome = iw
        self.finalIncome = fw
        self.workExperience = we
        self.careNeedLevel = 0
        self.socialWork = 0
        # Unmet Need variables 
        self.careDemand = 0
        self.unmetCareNeed = 0
        self.cumulativeUnmetNeed = 0
        self.totalDiscountedShareUnmetNeed = 0
        self.averageShareUnmetNeed = 0
        self.totalDiscountedTime = 0
        
        self.classRank = cr
        self.parentsClassRank = pcr
        self.dead = False
        self.partner = None
        if sex == 'random':
            self.sex = random.choice(['male', 'female'])
        else:
            self.sex = sex
        self.house = house
        self.houseID = -1 # For pickle
        self.sec = sec
        
        self.careAvailable = 0
        self.residualSupply = 0
        self.movedThisYear = False
        
        # Kinship network variables
        self.hoursChildCareDemand = 0
        self.netChildCareDemand = 0
        self.unmetChildCareNeed = 0
        self.hoursSocialCareDemand = 0
        self.unmetSocialCareNeed = 0
        self.informalChildCareReceived = 0
        self.formalChildCareReceived = 0
        self.publicChildCareContribution = 0
        self.informalSocialCareReceived = 0
        self.formalSocialCareReceived = 0
        self.childWork = 0
        self.socialWork = 0
        self.outOfWorkChildCare = 0
        self.outOfWorkSocialCare = 0
        self.residualWorkingHours = 0
        self.availableWorkingHours = 0
        self.residualInformalSupplies = [0.0, 0.0, 0.0, 0.0]
        self.residualInformalSupply = 0
        self.hoursInformalSupplies = [0.0, 0.0, 0.0, 0.0]
        self.maxFormalCareSupply = 0
        self.totalSupply = 0
        self.informalSupplyByKinship = [0.0, 0.0, 0.0, 0.0]
        self.formalSupplyByKinship = [0.0, 0.0, 0.0, 0.0]
        self.careForFamily = False
        
        
        self.id = Person.counter
        Person.counter += 1

class Population:
    """The population class stores a collection of persons."""
    def __init__ (self, initial, startYear, minStartAge, maxStartAge,
                  workingAge, incomeInitialLevels, incomeFinalLevels,
                  incomeGrowthRate, workDiscountingTime, wageVar, weeklyHours):
        self.allPeople = []
        self.livingPeople = []
        for i in range(int(initial)/2):
            ageMale = random.randint(minStartAge, maxStartAge)
            ageFemale = ageMale - random.randint(-2,5)
            if ( ageFemale < 24 ):
                ageFemale = 24
            birthYear = startYear - random.randint(minStartAge,maxStartAge)
            classes = [0, 1, 2, 3, 4]
            probClasses = [0.2, 0.35, 0.25, 0.15, 0.05]
            classRank = np.random.choice(classes, p = probClasses)
            
            workingTime = 0
            for i in range(int(ageMale)-int(workingAge[classRank])):
                workingTime *= workDiscountingTime
                workingTime += 1
            
            dKi = np.random.normal(0, wageVar)
            initialWage = incomeInitialLevels[classRank]*math.exp(dKi)
            dKf = np.random.normal(dKi, wageVar)
            finalWage = incomeFinalLevels[classRank]*math.exp(dKf)
            
            c = np.math.log(initialWage/finalWage)
            wage = finalWage*np.math.exp(c*np.math.exp(-1*incomeGrowthRate[classRank]*workingTime))
            income = wage*weeklyHours
            workExperience = workingTime
            newMan = Person(None, None,
                            birthYear, ageMale, 'male', None, None, classRank, classRank, wage, income, 0, initialWage, finalWage, workExperience, 'worker', True)
            
            workingTime = 0
            for i in range(int(ageFemale)-int(workingAge[classRank])):
                workingTime *= workDiscountingTime
                workingTime += 1
                
            dKi = np.random.normal(0, wageVar)
            initialWage = incomeInitialLevels[classRank]*math.exp(dKi)
            dKf = np.random.normal(dKi, wageVar)
            finalWage = incomeFinalLevels[classRank]*math.exp(dKf)
            
            c = np.math.log(initialWage/finalWage)
            wage = finalWage*np.math.exp(c*np.math.exp(-1*incomeGrowthRate[classRank]*workingTime))
            income = wage*weeklyHours
            workExperience = workingTime
            newWoman = Person(None, None,
                              birthYear, ageFemale, 'female', None, None, classRank, classRank, wage, income, 0, initialWage, finalWage, workExperience, 'worker', True)

            # newMan.status = 'independent adult'
            # newWoman.status = 'independent adult'
            
            newMan.partner = newWoman
            newWoman.partner = newMan
            
            self.allPeople.append(newMan)
            self.livingPeople.append(newMan)
            self.allPeople.append(newWoman)
            self.livingPeople.append(newWoman)

            
