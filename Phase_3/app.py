from flask import Flask, render_template, request,url_for
#from flask_mysqldb import MySQL
import MySQLdb
import pandas as pd
import numpy as np
import pymysql

db = pymysql.connect(host="localhost",  
                     port=3307,
                     user="root",        
                     passwd="root", 
                     db="cs6400_2021_01_Team030") 


app = Flask(__name__)
# todo: 1. add check constraint on create table sql schema, 2. add error-handing 3, group run sql together?

@app.route('/view_holiday',methods=['GET', 'POST'])
def view_holiday():
    cur = db.cursor()
    cur.execute("SELECT day, holiday FROM holiday")
    res = list(cur.fetchall())
    if request.method=='POST':
        message = ''
        d = request.form.get('date')
        h = request.form.get('holiday')
        query = f"""INSERT holiday (date, holiday)
                    VALUES ('{d}','{h}');
                     commit;
                  """
        if d and h:
            try:
                code = cur.execute(query)
                if code==1:
                    message = f"Successfully add {h} on {d}"
                    cur.execute("SELECT day, holiday FROM holiday")
                    res_new = list(cur.fetchall())
                    cur.close()
                    return render_template('view_holiday.html',holiday_list=res_new,message = message)
            except (MySQLdb.Error, MySQLdb.Warning) as e:
                message = e+'\n'
        message += "Insert fail, please input valid date and holiday name"
        cur.close() 
        return render_template('view_holiday.html',holiday_list=res,message = message)
    cur.close() 
    return render_template('view_holiday.html',holiday_list=res)


@app.route('/view_pop',methods=['GET', 'POST'])
def view_pop():
    cur = db.cursor()
    cur.execute("SELECT city_name, state, population, city_size FROM Population")
    res = list(cur.fetchall())
    if request.method=='POST':
        message = ''
        cityname = request.form.get('cityname')
        state = request.form.get('cityname')
        population = request.form.get('population')
        query = f"""UPDATE Population
                    SET population = {population},
                     city_size = CASE WHEN population<3700000 THEN 'Small'
                     WHEN population<6700000 THEN 'Medium'
                     WHEN population <9000000 THEN 'Large'
                     ELSE 'Extra Large' END
                     WHERE city_name = '{cityname}' and state = '{state}';
                     commit;
                  """
        if cityname and population and state:
            code = cur.execute(query)
            if code==1:
                message = f"Successfully update population for {cityname}, {state}"
                cur.execute("SELECT city_name, state,population, city_size FROM Population")
                res_new = list(cur.fetchall())
                cur.close()
                return render_template('view_pop.html',city_list=res_new,message = message)
        message = "Update fail, please input valid city name and population"
        cur.close() 
        return render_template('view_pop.html',city_list=res,message = message)
    cur.close() 
    return render_template('view_pop.html',city_list=res)

@app.route('/view_report1' ,methods=['GET'])
def view_report1():
    cur = db.cursor()
    query = """
    SELECT Category.Category_name, SUM(Product.PID), MIN(Product.regular_price), ROUND(AVG(Product.regular_price),2), MAX(Product.regular_price)
    FROM Category
    LEFT JOIN Product_Category ON Category.Category_name = Product_Category.Category_name
    LEFT JOIN Product ON Product_Category.PID = Product.PID
    GROUP BY Category_name
    ORDER BY Category_name ASC;
    """
    cur.execute(query)
    res = list(cur.fetchall())
    cur.close() 
    return render_template('view_report1.html',cat_list=res)

@app.route('/view_report2' ,methods=['GET'])
def view_report2():
    cur = db.cursor()
    query = """
    SELECT Actual_Revenue, Predicted_Revenue, (Actual_Revenue - Predicted_Revenue) AS diff 
    FROM(
    (
    SELECT (Revenue1+Revenue2) AS Actual_Revenue
    FROM(
    (
    SELECT SUM(quantity_sold*regular_price) AS Revenue1
    FROM(
    SELECT saleID, quantity_sold, day, sales.PID AS PID, product_name, regular_price, category_name
    FROM Sales, Product, product_category
    WHERE Sales.PID = Product.PID
    AND product_category.PID = sales.PID
    AND (Sales.PID, Sales.day) not in (SELECT PID, day FROM DiscountPrice)
    AND category_name = "Couches and Sofas") AS S
    )AS A,
    (
    SELECT SUM(quantity_sold*discount_price) AS Revenue2
    FROM(
    SELECT saleID, quantity_sold, sales.day AS day, sales.PID AS PID, product_name, discount_price, category_name
    FROM sales, product, discountprice, product_category
    WHERE Sales.PID = Product.PID
    AND product_category.PID = sales.PID
    AND Product.PID = DiscountPrice.PID
    AND Sales.day = DiscountPrice.day
    AND category_name = "Couches and Sofas") AS T
    )AS B
    ) 
    ) AS E,
    (
    SELECT SUM(quantity_sold*regular_price*0.75) AS Predicted_Revenue
    FROM(
    SELECT saleID, quantity_sold, day, sales.PID AS PID, product_name, regular_price, category_name
    FROM Sales, Product, product_category
    WHERE Sales.PID = Product.PID
    AND product_category.PID = sales.PID
    AND (Sales.PID, Sales.day) not in (SELECT PID, day FROM DiscountPrice)
    AND category_name = "Couches and Sofas") AS W
    ) AS F
    );
    """
    cur.execute(query)
    res = list(cur.fetchall())
    cur.close() 
    return render_template('view_report2.html',act_list=res)

@app.route('/view_report3',methods=['GET', 'POST'])
def view_report3_scripts():
    #create a cursor
    cur = db.cursor()
    # execute select statement to fetch data to be displayed in combo/dropdown
    cur.execute("""SELECT DISTINCT YEAR(sales.day)
                    FROM Sales
                    INNER JOIN Store ON Store.store_ID = Sales.store_ID""") 
    yearlist = sorted(list(set([_[0] for _ in cur.fetchall()] )))
    cur.execute("""SELECT DISTINCT Store.state
                    FROM Sales
                    INNER JOIN Store ON Store.store_ID = Sales.store_ID""") 
    statelist = sorted(list(set([_[0] for _ in cur.fetchall()] )))
    # Regular Revenue
    query_regRevenue = f"""
                    SELECT Store.store_ID, Store.street_address,Store.city_name, Store.state,
                    ROUND(SUM(quantity_sold *regular_price),2) AS regular_revenue,YEAR(sales.day) AS Year
                    FROM Sales, Product, product_category,Store
                    WHERE Sales.PID = Product.PID
                    AND product_category.PID = sales.PID
                    AND (Sales.PID, Sales.day) not in (SELECT PID, day FROM DiscountPrice)
                    AND Sales.store_ID = Store.store_ID
                    GROUP BY Store.store_ID, Year;
                  """
    cur.execute(query_regRevenue)
    rows = cur.fetchall()
    names = [ x[0] for x in cur.description]
    df_reg = pd.DataFrame( rows, columns=names)
    # Discounted Revenue
    query_disRevenue = """SELECT Store.store_ID, Store.street_address,Store.city_name, Store.state,
                            ROUND(SUM(quantity_sold *discount_price),2) AS discount_revenue,YEAR(sales.day) AS Year
                            FROM sales, product, discountprice, product_category, Store
                            WHERE Sales.PID = Product.PID
                            AND product_category.PID = sales.PID
                            AND Product.PID = DiscountPrice.PID
                            AND Sales.day = DiscountPrice.day
                            AND Sales.store_ID = Store.store_ID
                            GROUP BY Store.store_ID, Year;
                            """
    cur.execute(query_disRevenue)
    rows = cur.fetchall()
    names = [ x[0] for x in cur.description]
    df_dis = pd.DataFrame( rows, columns=names)
    # Merge
    df = pd.merge(left = df_reg, 
                    right = df_dis, 
                    how = 'outer',
                    on = ['store_ID','street_address','city_name','state','Year'])
    df['discount_revenue'] = df['discount_revenue'].fillna(0)
    df['regular_revenue'] = df['regular_revenue'].fillna(0)
    df['Revenue'] = df['discount_revenue']+df['regular_revenue']
    df['Revenue'] = df['Revenue'].round(2)
    df = df[['store_ID','street_address','city_name','state','Revenue','Year']]
    df = df.sort_values(['Year', 'Revenue'], ascending=[True, False])

    # Filter's on
    if request.method=='POST':
        state_selected = request.form.get('state_selected') 
        year_selected = request.form.get('year_selected') 
        # Filter

        df = df[(df['state'] == state_selected) & (df['Year'] == int(year_selected))]
        # Output
        revenue_list = df.values.tolist()
        cur.close() 
        return render_template("view_report3.html", statelist = statelist,
                                                    revenue_list = revenue_list,
                                                    yearlist = yearlist
                                                    )
    revenue_list = df.values.tolist()  
    cur.close()      
    return render_template("view_report3.html", statelist = statelist,
                                                yearlist = yearlist
                                                )


@app.route('/view_report4' ,methods=['GET'])
def view_report4():
    cur = db.cursor()
    query = """
    SELECT groudhogday_furniture_sold, total_sold, avg_sold, S.yr
    FROM (
    SELECT SUM(quantity_sold) AS groudhogday_furniture_sold, Year(day) AS yr
    FROM sales
    INNER JOIN product_category ON product_category.PID = sales.PID 
    WHERE product_category.category_name = "outdoor furniture" or "outdoor furnitureB" 
    AND Month(day) = 2 AND Day(day) = 2 
    GROUP BY Year(day)
    ) AS S
    INNER JOIN (
    SELECT Year(day) AS yr, SUM(quantity_sold) AS total_sold, (SUM(quantity_sold)/365) AS avg_sold
    FROM (
    SELECT saleID, quantity_sold, day, sales.PID AS PID, category_name
    FROM sales 
    INNER JOIN product_category ON product_category.PID = sales.PID 
    WHERE Product_Category.category_name = "outdoor furniture" or "outdoor furnitureB"
    ) AS T
    GROUP BY Year(day)
    ) AS T
    ON S.yr = T.yr
    ORDER BY S.yr ASC; 
    """
    cur.execute(query)
    res = list(cur.fetchall())
    cur.close() 
    return render_template('view_report4.html',out_list=res)

@app.route('/view_report5',methods=['GET', 'POST'])
def view_report5_scripts():
    #create a cursor
    cur = db.cursor()
    #execute select statement to fetch data to be displayed in combo/dropdown
    cur.execute("""SELECT DISTINCT YEAR(Sales.day) AS Year,MONTH(Sales.day) AS Month FROM Sales
                    """) 
    #fetch all rows ans store as a set of tuples 
    results = cur.fetchall()
    yearlist = sorted(list(set([_[0] for _ in results])))
    monthlist = sorted(list(set([_[1] for _ in results] )))
    # default: blank
    result_list = []
    # Filter's on
    if request.method=='POST':
        year_selected = request.form.get('year_selected')
        month_selected = request.form.get('month_selected')
        #print(year_selected,month_selected)
        query = f"""
                SELECT
                    Product_Category.category_name,
                    SUM(Sales.quantity_sold) AS state_total_sold,
                    YEAR(Sales.day) AS Year,
                    MONTH(Sales.day) AS Month,
                    Store.state
                FROM
                    Sales
                LEFT JOIN Product_Category ON Sales.PID = Product_Category.PID
                LEFT JOIN Store ON Store.store_ID = Sales.store_ID
                WHERE YEAR(Sales.day) = {year_selected} 
                    AND MONTH(Sales.day) = {month_selected}
                GROUP BY
                    Store.state,
                    Product_Category.category_name,
                    Year(Sales.day),
                    Month(Sales.day)
                ORDER BY category_name ASC,state_total_sold DESC
                """
        cur.execute(query)
        rows = cur.fetchall()
        names = [ x[0] for x in cur.description]
        df = pd.DataFrame( rows, columns=names)
        #print(df)
        df = df.groupby('category_name').head(1).reset_index(drop=True)
        result_list = df.values.tolist()
        cur.close()
        return render_template("view_report5.html", yearlist = yearlist,
                                                    monthlist = monthlist,
                                                    result_list=result_list)
    return render_template("view_report5.html", yearlist = yearlist,
                                                    monthlist = monthlist,
                                                    result_list=result_list)

@app.route('/view_report2_YC',methods=['GET'])
def view_report2_YC_scripts():
    #create a cursor
    cur = db.cursor()
    query_regRevenue = """
                SELECT Product.PID, Category.category_name,quantity_sold,regular_price
                ROUND(SUM(quantity_sold *regular_price),2) AS regular_revenue,sales.day
                FROM Sales, Product, product_category,Store,Population
                WHERE Sales.PID = Product.PID
                AND product_category.category_name = Category.category_name
                AND product_category.PID = sales.PID
                AND (Sales.PID, Sales.day) not in (SELECT PID, day FROM DiscountPrice)
                AND Sales.store_ID = Store.store_ID
                AND Population.city_name = Store.city_name
                GROUP BY Year,Population.city_size, Store.store_ID
                """
    cur.execute(query_regRevenue)
    rows = cur.fetchall()
    names = [ x[0] for x in cur.description]
    df_reg = pd.DataFrame( rows, columns=names)
    # Discounted Revenue
    query_disRevenue = """
                        SELECT Store.store_ID, Store.street_address,Store.city_name, Population.city_size,
                        ROUND(SUM(quantity_sold*1.25 *discount_price),2) AS discount_revenue,YEAR(sales.day) AS Year
                        FROM sales, product, discountprice, product_category, Store, Population
                        WHERE Sales.PID = Product.PID
                        AND product_category.PID = sales.PID
                        AND Product.PID = DiscountPrice.PID
                        AND Sales.day = DiscountPrice.day
                        AND Sales.store_ID = Store.store_ID
                        AND Store.city_name = Population.city_name
                        GROUP BY Population.city_size, Store.store_ID, Year;
                        """
    cur.execute(query_disRevenue)
    rows = cur.fetchall()
    names = [ x[0] for x in cur.description]
    df_dis = pd.DataFrame( rows, columns=names)
    # Merge
    df = pd.merge(left = df_reg, 
                right = df_dis, 
                how = 'outer',
                on = ['store_ID','street_address','city_name','city_size','Year'])
    df['discount_revenue'] = df['discount_revenue'].fillna(0)
    df['regular_revenue'] = df['regular_revenue'].fillna(0)
    df['Revenue'] = df['discount_revenue']+df['regular_revenue']
    df = pd.pivot_table(df, values='Revenue', index=['Year'],
                        columns=['city_size'], aggfunc=np.sum)
    df = df[['Small', 'Medium', 'Large','Extra Large']].fillna(0)
    result_list = df.values.tolist()
    cur.close()
    return render_template("view_report6.html", result_list=result_list)


    #create a cursor
    cur = db.cursor()
    query_regRevenue = """
SELECT
    Product.PID, Product.product_name, product_category.category_name, quantity_sold, regular_price,
    ROUND(SUM(quantity_sold * regular_price),2) AS regular_revenue,sales.day
FROM
    Sales,Product,product_category
WHERE
    Sales.PID = Product.PID 
    AND product_category.PID = sales.PID 
    AND(Sales.PID, Sales.day) NOT IN(
    SELECT PID, DAY FROM DiscountPrice) AND product_category.Category_name = 'Couches and Sofas'
GROUP BY
    Product.PID, Product.product_name,product_category.category_name,quantity_sold,regular_price,sales.day
                """
    cur.execute(query_regRevenue)
    rows = cur.fetchall()
    names = [ x[0] for x in cur.description]
    df_reg = pd.DataFrame( rows, columns=names)
    # Discounted Revenue
    query_predRevenue = """
                        SELECT
    Product.PID, Product.product_name, product_category.category_name, quantity_sold*0.75 AS predicted_quantity_sold, discount_price,
    ROUND(SUM(quantity_sold*0.75 * discount_price),2) AS predicted_revenue,sales.day
FROM
    Sales,Product,product_category,discountprice
WHERE
    Sales.PID = Product.PID 
    AND product_category.PID = sales.PID 
    AND Product.PID = DiscountPrice.PID
    AND Sales.day = DiscountPrice.day
                        
    AND(Sales.PID, Sales.day) NOT IN(
    SELECT PID, DAY FROM DiscountPrice) AND product_category.Category_name = 'Couches and Sofas'
GROUP BY
    Product.PID, Product.product_name,product_category.category_name,discounted_quantity_sold,discount_price,sales.day;
                        """
    cur.execute(query_disRevenue)
    rows = cur.fetchall()
    names = [ x[0] for x in cur.description]
    df_pred = pd.DataFrame( rows, columns=names)
    # Merge
    df = pd.merge(left = df_reg, 
                right = df_pred, 
                how = 'outer',
                on = ['PID','product_name','category_name','day'])
    df['predicted_quantity_sold'] = df['predicted_quantity_sold'].fillna(0)
    df['discount_price'] = df['discount_price'].fillna(0)
    df['predicted_revenue'] = df['predicted_revenue'].fillna(0)
    df['regular_quantity_sold'] = df['regular_quantity_sold'].fillna(0)
    df['regular_price'] = df['regular_price'].fillna(0)
    df['regular_revenue'] = df['regular_revenue'].fillna(0)

    df['difference_in_revenue'] = df['predicted_revenue']-df['regular_quantity_sold']
    df=df[(df['difference_in_revenue']>5000) or (df['difference_in_revenue']<5000)]
    result_list = df.values.tolist()
    cur.close()
    return render_template("view_report2_YC.html", result_list=result_list)








  
@app.route('/view_report7',methods=['GET'])
def view_report7():
    cur = db.cursor()
    cur.execute('SELECT DISTINCT(childcare_limit) FROM store')
    care_level = [c[0] for c in list(cur.fetchall())]
    query = """
    WITH sale_data AS(
    SELECT month, childcare_limit, SUM(total_sold) as total_sales
    FROM (
    SELECT MONTH(Sales.day) as month, Store.childcare_limit, SUM(Sales.quantity_sold*Product.regular_price) AS total_sold
FROM Sales, Product, Store
WHERE Sales.PID = Product.PID
	AND Sales.store_ID = Store.store_ID
    AND (Sales.PID, Sales.day) not in (SELECT PID, day FROM DiscountPrice)
    AND DATEDIFF(NOW(),Sales.day)<=365*10 
GROUP BY 1,2
UNION ALL
SELECT MONTH(Sales.day) as month, Store.childcare_limit, SUM(Sales.quantity_sold* discountprice.discount_price) AS total_sold
FROM Sales, Product, Store, DiscountPrice
WHERE Sales.PID = Product.PID
	AND Sales.store_ID = Store.store_ID
    AND Product.PID = DiscountPrice.PID
    AND Sales.day = DiscountPrice.day
    AND DATEDIFF(NOW(),Sales.day)<=365*10 
GROUP BY 1,2) t
GROUP BY 1,2
ORDER BY 1,2)

SELECT month
"""
    col_list = []
    for c in care_level:
        if c == 0:
            col_name = 'No_childcare'
        else:
            col_name = 'Childcare_'+str(c)+'_min'
        query+= f',SUM(CASE WHEN childcare_limit = {c} THEN total_sales ELSE 0 END) AS "{col_name}"'
        col_list.append(col_name)
    query += " FROM sale_data GROUP BY 1 ORDER BY 1"
    
    cur.execute(query)
    res = list(cur.fetchall())
    print(res) 
    cur.close()
    return render_template('view_report7.html',clevel =col_list ,res_list=res)


@app.route('/view_report8' ,methods=['GET'])
def view_report8():
    cur = db.cursor()
    query = """
    WITH store_sale_cat AS(
    SELECT Store.store_ID, Product_Category.category_name as category_name,
    SUM(Sales.quantity_sold) as total_sold
    FROM Store
    INNER JOIN Sales ON Store.store_ID = Sales.store_ID
    INNER JOIN Product ON Sales.PID = Product.PID
    INNER JOIN Product_Category ON Product.PID = Product_Category.PID
    GROUP BY Store.store_ID, Product_Category.category_name),
    store_res AS(SELECT Store.Store_ID FROM Store WHERE Store.restaurant = 1),

    res_non AS(
    SELECT t.category_name, SUM(t.quantity_sold1) as qs1, SUM(t.quantity_sold2) as qs2   
    FROM(
    
    SELECT *
    FROM(
    SELECT store_sale_cat.category_name, SUM(total_sold) as quantity_sold1, 0 as quantity_sold2
    FROM store_sale_cat
    WHERE store_sale_cat.store_ID IN (SELECT * FROM store_res) 
    GROUP BY store_sale_cat.category_name) t1

    UNION ALL
    
    SELECT *
    FROM(
    SELECT store_sale_cat.category_name, 0 as quantity_sold1, SUM(total_sold) as quantity_sold2 
    FROM store_sale_cat
    WHERE store_sale_cat.store_ID NOT IN (SELECT * FROM store_res)
    GROUP BY store_sale_cat.category_name) t2
        
    ) t
    GROUP BY t.category_name
    ORDER BY t.category_name
    )
        
    
    SELECT t1.category_name, t1.st, t1.qs
    FROM(
    SELECT res_non.category_name, 'Restaurant' as st, res_non.qs1 as qs
    FROM res_non
    
    UNION ALL
        
    SELECT res_non.category_name, 'Non-Restaurant' as st, res_non.qs2 as qs
    FROM res_non
    ) t1
    ORDER BY t1.category_name, t1.st;
    """
    cur.execute(query)
    res = list(cur.fetchall())
    cur.close() 
    return render_template('view_report8.html',resimp_list=res)

@app.route('/view_report9' ,methods=['GET'])
def view_report9():
    cur = db.cursor()
    query = """
    WITH sale_items AS
    (SELECT Product.PID, DiscountPrice.day AS sale_date,
    DiscountPrice.discount_price AS sale_price
    FROM Product
    INNER JOIN DiscountPrice ON DiscountPrice.PID = Product.PID
    WHERE DiscountPrice.day in (SELECT AdCampaign.day FROM AdCampaign WHERE
    AdCampaign.ad_compaign_description IS NOT NULL)
    ),

    campaign_sold AS
    (SELECT sale_items.PID, SUM(Sales.quantity_sold) as total_sale_quantity, 0 as total_reg_quantity
    FROM Sales, sale_items
    WHERE Sales.PID = sale_items.PID
    AND Sales.day = sale_items.sale_date
    GROUP BY sale_items.PID),

    regular_sold AS
    (SELECT sale_items.PID, 0 as total_sale_quantity, SUM(Sales.quantity_sold) as total_reg_quantity
    FROM Sales, sale_items
    WHERE Sales.PID = sale_items.PID
    AND Sales.day != sale_items.sale_date
    AND Sales.day in (SELECT DiscountPrice.day FROM Sales INNER JOIN DiscountPrice ON Sales.PID = DiscountPrice.PID)
    GROUP BY sale_items.PID),

    Diff as
    (SELECT t1.PID AS PID, SUM(t1.total_sale_quantity) AS tsq, SUM(t1.total_reg_quantity) AS trq,
    (SUM(t1.total_sale_quantity) - SUM(t1.total_reg_quantity)) AS difference
    FROM(
    SELECT * FROM campaign_sold 
   	UNION 
    SELECT * FROM regular_sold
    ) t1
    GROUP BY t1.PID)

    SELECT *
    FROM(        
    SELECT *
    FROM(
    SELECT Diff.PID, product_name, tsq, trq, difference
    FROM Diff
    JOIN Product ON Diff.PID = Product.PID
    ORDER BY Diff.difference DESC LIMIT 10) t_top
    UNION
    SELECT *
    FROM(
    SELECT Diff.PID, product_name, tsq, trq, difference
    FROM Diff
    JOIN Product ON Diff.PID = Product.PID
    ORDER BY Diff.difference LIMIT 10) t_down
    ) t
    ORDER BY difference DESC;
    """
    cur.execute(query)
    res = list(cur.fetchall())
    cur.close() 
    return render_template('view_report9.html',aca_list=res)

def generate_stat():
    res = []
    cur = db.cursor()
    directory = "./overview_stats/"
    q_list = [i for i in os.listdir(directory) if i.endswith('sql')]
    for q in q_list:
        file = directory + q
        with open(file, 'r') as sql_file:
            cur.execute(sql_file.read())
            r = [q.split(".")[0]] + [cur.fetchall()[0][0]]
            res.append(r)
    cur.close()
    return res

@app.route('/', methods=['GET'])
def home():
    stat = generate_stat()
    return render_template('view_stats.html', stat_list=stat)

if __name__ == '__main__':
    app.run()

# 
# if __name__ == '__main__':
#     app.run(debug=True)
