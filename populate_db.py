from app import db
# from app.models import Student, Teacher, Course, Grade, User

from app.models import Users

def populate_db():
    """Populates the cscourses.db database if it is empty. The Flask app needs to be running before you execute this code.

    :return: None
    """

    if not Recipes.query.first():

        r1 = Recipes(recipe_name="Banana & blueberry muffins", photo="", serves=12, cook_time=20, prep_time=10,
                     total_time=30)
        r2 = Recipes(recipe_name="Make-ahead mushroom souffles", photo="", serves=8, cook_time=30, prep_time=30,
                     total_time=60)
        r3 = Recipes(recipe_name="Chinese steamed bass with cabbage", photo="", serves=2, cook_time=10, prep_time=10,
                     total_time=20)
        r4 = Recipes(recipe_name="Thai green pork lettuce cups", photo="", serves=4, cook_time=15, prep_time=10,
                     total_time=25)
        r5 = Recipes(recipe_name="Roasted spirce cauliflower", photo="", serves=4, cook_time=60, prep_time=10,
                     total_time=70)

        ri0 = RecipeIngredients(recipe_id=0, ingredient="300g self-raising flour")
        ri1 = RecipeIngredients(recipe_id=0, ingredient="1 tsp bicarbonate of soda")
        ri2 = RecipeIngredients(recipe_id=0, ingredient="100g light muscovado sugar")
        ri3 = RecipeIngredients(recipe_id=0, ingredient="50g porridge oat, plus 1 tbsp for topping")
        ri4 = RecipeIngredients(recipe_id=0, ingredient="2 medium bananas, the riper the better")
        ri5 = RecipeIngredients(recipe_id=0, ingredient="284ml carton buttermilk")
        ri6 = RecipeIngredients(recipe_id=0, ingredient="5 tbsp light olive oil")
        ri7 = RecipeIngredients(recipe_id=0, ingredient="2 egg whites")
        ri8 = RecipeIngredients(recipe_id=0, ingredient="150g punnet blueberries")
        ri9 = RecipeIngredients(recipe_id=1, ingredient="140g small button mushroom, sliced")
        ri10 = RecipeIngredients(recipe_id=1, ingredient="50g butter, plus extra for greasing")
        ri11 = RecipeIngredients(recipe_id=1, ingredient="25g plain flour")
        ri12 = RecipeIngredients(recipe_id=1, ingredient="325ml milk")
        ri13 = RecipeIngredients(recipe_id=1, ingredient="85g gruyère, finely grated, plus a little extra")
        ri14 = RecipeIngredients(recipe_id=1, ingredient="3 large eggs, separated")
        ri15 = RecipeIngredients(recipe_id=1, ingredient="6 tsp crème fraîche")
        ri16 = RecipeIngredients(recipe_id=1, ingredient="snipped chive, to serve")
        ri17 = RecipeIngredients(recipe_id=2, ingredient="250g puy lentils")
        ri18 = RecipeIngredients(recipe_id=2, ingredient="2 shallots, finely chopped")
        ri19 = RecipeIngredients(recipe_id=2, ingredient="4 tbsp olive oil")
        ri20 = RecipeIngredients(recipe_id=2, ingredient="140g shiitake mushroom, quartered")
        ri21 = RecipeIngredients(recipe_id=2, ingredient="250g pack cherry or plum tomatoes, halved")
        ri22 = RecipeIngredients(recipe_id=2, ingredient="2 tbsp capers, rinsed")
        ri23 = RecipeIngredients(recipe_id=2, ingredient="150ml white wine")
        ri24 = RecipeIngredients(recipe_id=2, ingredient="4 x brill (or any other white fish like cod) fillets, skinned - about 140-175g/5-6oz each")
        ri25 = RecipeIngredients(recipe_id=2, ingredient="1 small lemon, thinly sliced")
        ri26 = RecipeIngredients(recipe_id=2, ingredient="1 small bunch of flat-leaf parsley, roughly chopped")
        ri27 = RecipeIngredients(recipe_id=2, ingredient="140g baby spinach leaves")

        rins1 = RecipeInstructions(recipe_id=0, step_num=1, step_description="Heat oven to 180C/fan 160C/gas 4 and line a 12-hole muffin tin with paper muffin cases. Tip the flour and bicarbonate of soda into a large bowl. Hold back 1 tbsp of the sugar, then mix the remainder with the flour and 50g oats. Make a well in the centre. In a separate bowl, mash the bananas until nearly smooth. Stir the buttermilk, oil and egg whites into the mashed banana until evenly combined.")
        rins2 = RecipeInstructions(recipe_id=0, step_num=2, step_description="Pour the liquid mixture into the well and stir quickly and sparingly with a wooden spoon. The mix will look lumpy and may have the odd fleck of flour still visible, but don’t be tempted to over-mix. Tip in the blueberries and give it just one more stir. Divide the mix between the muffin cases – they will be quite full – then sprinkle the tops with the final tbsp of the oats and the rest of he sugar. Bake for 18-20 mins until risen and dark golden. Cool for 5 mins in the tray before lifting out onto a rack to cool completely.")
        rins3 = RecipeInstructions(recipe_id=1, step_num=1, step_description="Fry the mushrooms in the butter for about 3 mins, then remove from the heat and reserve a good spoonful. Add the flour to the rest, then blend in the milk and return to the heat, stirring all the time to make a thick sauce. Stir in the cheese, season to taste, then leave to cool.")
        rins4 = RecipeInstructions(recipe_id=1, step_num=2, step_description="Heat oven to 200C/fan 180C/gas 6. Butter 8 x 150ml soufflé dishes and line the bases with baking paper. Stir the egg yolks into the soufflé mixture, then whisk the egg whites until stiff before folding in carefully. Spoon into the soufflé dishes and bake in a roasting tin, half-filled with cold water, for 15 mins until risen and golden. Leave to cool (they will sink, but they are meant to). You can make the soufflés up to this stage up to 2 days ahead. Cover and chill.")
        rins5 = RecipeInstructions(recipe_id=1, step_num=3, step_description="When ready to serve, turn the soufflés out of their dishes, peel off the lining paper, then put them on a baking sheet lined with small squares of baking paper. Top each soufflé with 1 tsp crème fraîche and a little cheese, then scatter with the reserved mushrooms. Bake at 190C/fan 170C/gas 5 for 10-15 mins until slightly risen and warmed through. Sprinkle with chives and serve.")
        rins6 = RecipeInstructions(recipe_id=2, step_num=1, step_description="Heat oven to 200C/fan oven 180C/gas mark 6. Tip the lentils into a pan, and cover with cold water. Bring to the boil and cook for 15-20 mins until they are tender. Drain and keep to one side.")
        rins7 = RecipeInstructions(recipe_id=2, step_num=2, step_description="Fry the shallots in half the oil in a shallow roasting tray on top of the hob, until softened. Increase the heat and add the mushrooms. Cook for a couple of minutes, until they are colouring around the edges. Remove the tray from the heat, then stir in the cooked lentils, halved tomatoes, capers and wine.")
        rins8 = RecipeInstructions(recipe_id=2, step_num=3, step_description="Sit the fish on the lentils then top with a couple of slices of lemon and drizzle over the remaining oil. Season everything with flaked sea salt and freshly ground black pepper. Roast for 15 mins – until the fish is cooked through and beginning to go golden on top.")
        rins9 = RecipeInstructions(recipe_id=2, step_num=4, step_description="Gently lift fish from the tray. Stir the parsley and spinach into lentils, until the spinach starts to wilt. Spoon onto 4 plates, sit the fish on top and serve.")

        nv1 = NutritionValues(recipe_id=0, calories=202, fats=5, saturates=0.8, carbs=36, sugars=14, fibres=2, proteins=5, salts=0.59)
        nv2 = NutritionValues(recipe_id=1, calories=170, fats=14, saturates=8, carbs=5, sugars=2, fibres=0, proteins=8, salts=0.41)
        nv3 = NutritionValues(recipe_id=2, calories=471, fats=17, saturates=2, carbs=34, sugars=0, fibres=7, proteins=42, salts=0.67)



        db.session.add_all([r1, r2, r3])
        db.session.add_all([ri0, ri1, ri2, ri3, ri4, ri5, ri6, ri7, ri8, ri9, ri10, ri11, ri12, ri13, ri14, ri15, ri16, ri17, ri18, ri19, ri20, ri21, ri22, ri23, ri24, ri25, ri26, ri27])
        db.session.add_all([rins1, rins2, rins3, rins4, rins5, rins6, rins7, rins8, rins9])
        db.session.add_all([nv1, nv2, nv3])
        db.session.commit()

    if not Users.query.first():
        pass
        # Example user for mealtime
        # u1 = User(first_name="John", last_name="Wayne", email="johnwayne@googlemail.com", password="")
        # u2 = User(first_name="Thomas", last_name="The Tank Engine", email="thomas@bbc.co.uk", password="")

        # s1 = Student(email="cs1234567@ucl.ac.uk", password="cs1234567", student_ref="CS1234567", name="Ahmet Roth")
        # s2 = Student(email="cs1234568@ucl.ac.uk", password="cs1234568", user_type="student", student_ref="CS1234568", name="Elsie-Rose Kent")
        # s3 = Student(email="cs1234569@ucl.ac.uk", password="cs1234569", user_type="student", student_ref="CS1234569", name="Willem Bull")
        # s4 = Student(email="cs1234570@ucl.ac.uk", password="cs1234570", user_type="student", student_ref="CS1234570", name="Jago Curtis")
        # s5 = Student(email="cs1234571@ucl.ac.uk", password="cs1234571", user_type="student", student_ref="CS1234571", name="Mateusz Bauer")
        # s6 = Student(email="cs1234572@ucl.ac.uk", password="cs1234572", user_type="student", student_ref="CS1234572", name="Morwenna Shepherd")
        #
        # t1 = Teacher(email="ct0000123@ucl.ac.uk", password="ct0000123", user_type="teacher", teacher_ref="uclcs0002", title="Dr", name="Lewis Baird")
        # t2 = Teacher(email="ct0000124@ucl.ac.uk", password="ct0000124", user_type="teacher", teacher_ref="uclcs0006", title="Prof", name="Elif Munro")
        # t3 = Teacher(email="ct0000125@ucl.ac.uk", password="ct0000125", user_type="teacher", teacher_ref="uclcs0010", title="Ms", name="Aleyna Bonilla")
        # t4 = Teacher(email="ct0000126@ucl.ac.uk", password="ct0000126", user_type="teacher", teacher_ref="uclcs0072", title="Dr", name="Maximus Tierney")
        # t5 = Teacher(email="ct0000127@ucl.ac.uk", password="ct0000127", user_type="teacher", teacher_ref="uclcs0021", title="Dr", name="Marcelina McClure")
        # t6 = Teacher(email="ct0000128@ucl.ac.uk", password="ct0000128", user_type="teacher", teacher_ref="uclcs0132", title="Dr", name="Fei Hong Zhou")
        #
        # c1 = Course(course_code="COMP0015", name="Introduction to Programming")
        # c2 = Course(course_code="COMP0034", name="Software Engineering")
        # c3 = Course(course_code="COMP0035", name="Web Development")
        # c4 = Course(course_code="COMP0070", name="Algorithmics")
        # c5 = Course(course_code="COMP0068", name="Architecture and Hardware")
        # c6 = Course(course_code="COMP0022", name="Database and Information Management Systems")
        # c7 = Course(course_code="COMP0067", name="Design")
        # c8 = Course(course_code="COMP0066", name="Introductory Programming")
        # c9 = Course(course_code="COMP0039", name="Entrepreneurship: Theory and Practice")
        # c10 = Course(course_code="COMP0020", name="Functional Programming")
        # c11 = Course(course_code="COMP0021", name="Interaction Design")
        # c12 = Course(course_code="COMP0142", name="Machine Learning for Domain Specialists")
        # c13 = Course(course_code="COMP0142", name="Software Engineering")
        #
        # g1 = Grade(grade="B-")
        # g2 = Grade(grade="C")
        # g3 = Grade(grade="B+")
        # g4 = Grade(grade="A+")
        # g5 = Grade(grade="A+")
        # g6 = Grade(grade="D+")
        # g7 = Grade(grade="B")
        # g8 = Grade(grade="D-")
        #
        # s1.grades.append(g1)
        # s1.grades.append(g5)
        # s2.grades.append(g2)
        # s2.grades.append(g6)
        # s3.grades.append(g3)
        # s3.grades.append(g7)
        # s4.grades.append(g4)
        # s4.grades.append(g8)
        #
        # c1.grades.append(g1)
        # c1.grades.append(g2)
        # c1.grades.append(g3)
        # c1.grades.append(g4)
        # c2.grades.append(g5)
        # c2.grades.append(g6)
        # c2.grades.append(g7)
        # c2.grades.append(g8)
        #
        # t1.courses.append(c1)
        # t2.courses.append(c2)
        # t3.courses.append(c3)
        # t4.courses.append(c4)
        # t5.courses.append(c5)
        # t6.courses.append(c6)
        # t6.courses.append(c7)
        # t6.courses.append(c8)
        # t1.courses.append(c9)
        # t2.courses.append(c10)
        # t3.courses.append(c11)
        # t5.courses.append(c12)
        # t5.courses.append(c13)
        #
        # db.session.add_all([s1, s2, s3, s4, s5, s6])
        # db.session.add_all([t1, t2, t3, t4, t5, t6])
        # db.session.commit()
