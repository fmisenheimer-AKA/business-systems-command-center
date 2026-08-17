
from flask import Flask, request, jsonify, render_template_string
import sqlite3, os, time
from datetime import datetime

app = Flask(__name__)
DB = os.path.join(os.path.dirname(__file__), "portfolio.db")

ITEMS = {
    "DEMO-WATER-FILTER": {"name":"Personal Water Filter","price":19.95,"reorder_point":500,"preferred_stock":1500},
    "DEMO-HOME-PITCHER": {"name":"Home Water Filter Pitcher","price":54.95,"reorder_point":300,"preferred_stock":1000},
    "DEMO-REPLACEMENT": {"name":"Replacement Filter","price":24.95,"reorder_point":400,"preferred_stock":1200},
}

HTML = r"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Felicia Misenheimer | NetSuite Integration Demo</title>
<style>
body{font-family:Arial,Helvetica,sans-serif;margin:0;background:#f5f7f7;color:#172126}
header{background:#123b2a;color:white;padding:24px 30px}
header h1{margin:0;font-size:26px} header p{margin:6px 0 0;color:#d9e8df}
.container{max-width:1180px;margin:auto;padding:26px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
.card{background:white;border-radius:12px;padding:16px;box-shadow:0 2px 8px rgba(0,0,0,.06)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-top:16px}
.kpi{font-size:28px;font-weight:700;margin-top:8px}
.small{font-size:12px;color:#667085}
h2{font-size:18px;margin:0 0 12px}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:9px;border-bottom:1px solid #e6e9ec;text-align:left}
.ok{color:#087443;font-weight:700}.warn{color:#a15c00;font-weight:700}.bad{color:#b42318;font-weight:700}
input,select,button{padding:10px;border:1px solid #cfd6dc;border-radius:8px}
form{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}
button{background:#123b2a;color:white;cursor:pointer}
pre{background:#0f172a;color:#e6edf3;padding:12px;border-radius:10px;min-height:155px;overflow:auto}
.flow{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:16px}
.node{background:white;border:1px solid #d8e2dc;border-radius:10px;padding:9px 12px}
.arrow{color:#667085;font-weight:700}
@media(max-width:900px){.grid{grid-template-columns:repeat(2,1fr)}.two{grid-template-columns:1fr}}
</style>
</head>
<body>
<header>
<h1>Felicia Misenheimer — Business Systems Command Center</h1>
<p>Candidate work sample • Manager, IT & Business Systems • fictional data • simulated NetSuite lifecycle</p>
</header>
<div class="container">
<div class="flow">
  <div class="node">Commerce</div><div class="arrow">→</div>
  <div class="node">REST Integration</div><div class="arrow">→</div>
  <div class="node">NetSuite Sales Order</div><div class="arrow">→</div>
  <div class="node">Inventory</div><div class="arrow">→</div>
  <div class="node">3PL Fulfillment</div><div class="arrow">→</div>
  <div class="node">Invoice</div><div class="arrow">→</div>
  <div class="node">Replenishment</div>
</div>

<div class="grid">
  <div class="card"><div class="small">Orders</div><div class="kpi">{{k.orders}}</div></div>
  <div class="card"><div class="small">Fulfilled</div><div class="kpi">{{k.fulfilled}}</div></div>
  <div class="card"><div class="small">Open Exceptions</div><div class="kpi">{{k.exceptions}}</div></div>
  <div class="card"><div class="small">Integration Success</div><div class="kpi">{{k.success}}%</div></div>
</div>

<div class="two">
<div class="card">
<h2>Data Quality & AI Readiness</h2>
<table>
<tr><td>Data Quality Score</td><td class="ok">94.7%</td></tr>
<tr><td>Duplicate Customers</td><td class="warn">8</td></tr>
<tr><td>Missing Item Attributes</td><td class="warn">11</td></tr>
<tr><td>Warehouse Freshness</td><td class="ok">98%</td></tr>
<tr><td>AI Data Readiness</td><td class="ok">91%</td></tr>
</table>
</div>
<div class="card">
<h2>IT / Vendor / Spend Snapshot</h2>
<table>
<tr><td>Annual Demo Technology Spend</td><td>$248K</td></tr>
<tr><td>Illustrative Optimization</td><td class="ok">$31.2K</td></tr>
<tr><td>Vendors / Providers</td><td>4</td></tr>
<tr><td>Tools for Review</td><td class="warn">3</td></tr>
<tr><td>Privileged Access Risks</td><td class="warn">2</td></tr>
</table>
</div>
</div>

<div class="two">
<div class="card">
<h2>Create Demo Commerce Order</h2>
<form id="orderForm">
<input name="externalId" value="SHOP-DEMO-2001" placeholder="External ID">
<input name="customer" value="Demo Customer" placeholder="Customer">
<select name="sku">
<option>DEMO-WATER-FILTER</option>
<option>DEMO-HOME-PITCHER</option>
<option>DEMO-REPLACEMENT</option>
<option>INVALID-123</option>
</select>
<input name="quantity" type="number" value="25" min="1">
<button>Create NetSuite Sales Order</button>
</form>
<pre id="result">Submit a valid order or select INVALID-123 to trigger exception handling.</pre>
</div>

<div class="card">
<h2>Inventory & Replenishment</h2>
<table>
<tr><th>SKU</th><th>Available</th><th>Reorder</th><th>Status</th></tr>
{% for r in inventory %}
<tr><td>{{r[0]}}</td><td>{{r[1]}}</td><td>{{r[2]}}</td>
<td class="{{'warn' if r[1] < r[2] else 'ok'}}">{{'REPLENISH' if r[1] < r[2] else 'HEALTHY'}}</td></tr>
{% endfor %}
</table>
<p class="small">Low-stock items create a purchase-order recommendation in the simulated procurement flow.</p>
</div>
</div>

<div class="two">
<div class="card">
<h2>Recent NetSuite-Style Orders</h2>
<table>
<tr><th>External</th><th>SO</th><th>SKU</th><th>Qty</th><th>Status</th></tr>
{% for o in orders %}
<tr><td>{{o[0]}}</td><td>{{o[1]}}</td><td>{{o[2]}}</td><td>{{o[3]}}</td><td>{{o[4]}}</td></tr>
{% endfor %}
</table>
</div>

<div class="card">
<h2>Integration Exceptions</h2>
<table>
<tr><th>ID</th><th>Order</th><th>Error</th><th>Impact</th><th>Action</th></tr>
{% for e in exceptions %}
<tr><td>{{e[0]}}</td><td>{{e[1]}}</td><td class="bad">{{e[2]}}</td><td>{{e[3]}}</td>
<td><button onclick="retryException({{e[0]}})">Retry</button></td></tr>
{% endfor %}
</table>
</div>
</div>

<div class="two">
<div class="card">
<h2>3PL / Invoice Lifecycle</h2>
<table>
<tr><th>Sales Order</th><th>Fulfillment</th><th>Invoice</th><th>Status</th></tr>
{% for f in fulfillment %}
<tr><td>{{f[0]}}</td><td>{{f[1]}}</td><td>{{f[2]}}</td><td class="ok">{{f[3]}}</td></tr>
{% endfor %}
</table>
</div>

<div class="card">
<h2>Integration Event Log</h2>
<table>
<tr><th>Time</th><th>Event</th><th>Reference</th><th>Status</th></tr>
{% for l in logs %}
<tr><td>{{l[0]}}</td><td>{{l[1]}}</td><td>{{l[2]}}</td><td>{{l[3]}}</td></tr>
{% endfor %}
</table>
</div>
</div>

<div class="two">
<div class="card">
<h2>Integration Control Center</h2>
<table>
<tr><th>Integration</th><th>Success</th><th>Failed</th><th>Last Sync</th></tr>
<tr><td>Shopify → NetSuite</td><td class="ok">99.8%</td><td>2</td><td>2 min</td></tr>
<tr><td>Amazon → NetSuite</td><td class="ok">99.5%</td><td>5</td><td>4 min</td></tr>
<tr><td>NetSuite → 3PL</td><td class="ok">99.9%</td><td>1</td><td>1 min</td></tr>
<tr><td>NetSuite → Analytics</td><td class="ok">100%</td><td>0</td><td>15 min</td></tr>
</table>
</div>
<div class="card">
<h2>NetSuite Access Governance</h2>
<table>
<tr><th>User</th><th>Role</th><th>Risk</th><th>Action</th></tr>
<tr><td>Demo Finance</td><td>Controller</td><td class="ok">LOW</td><td>Approve</td></tr>
<tr><td>Demo Ops</td><td>Inventory Manager</td><td class="ok">LOW</td><td>Approve</td></tr>
<tr><td>Demo Admin</td><td>Administrator</td><td class="warn">HIGH</td><td>Reduce / justify</td></tr>
<tr><td>Demo Vendor</td><td>Integration Role</td><td class="warn">MEDIUM</td><td>Restrict</td></tr>
<tr><td>Former User</td><td>Sales</td><td class="bad">HIGH</td><td>Disable</td></tr>
</table>
</div>
</div>

<div class="two">
<div class="card">
<h2>Technology Portfolio & Cost Optimization</h2>
<table>
<tr><th>System</th><th>Annual Cost</th><th>Utilization</th><th>Decision</th></tr>
<tr><td>NetSuite ERP</td><td>$92K</td><td>Core</td><td class="ok">KEEP</td></tr>
<tr><td>Integration Platform</td><td>$42K</td><td>High</td><td class="ok">KEEP</td></tr>
<tr><td>Analytics Platform</td><td>$28K</td><td>High</td><td class="ok">KEEP</td></tr>
<tr><td>Legacy Reporting</td><td>$16K</td><td>18%</td><td class="warn">REVIEW</td></tr>
<tr><td>Duplicate File Storage</td><td>$7.2K</td><td>Redundant</td><td class="bad">ELIMINATE</td></tr>
</table>
</div>
<div class="card">
<h2>Vendor / MSP Scorecard</h2>
<table>
<tr><th>Provider</th><th>Function</th><th>SLA</th><th>Action</th></tr>
<tr><td>Demo MSP</td><td>IT Support</td><td>97%</td><td>KEEP</td></tr>
<tr><td>Demo NetSuite Partner</td><td>ERP Consulting</td><td>95%</td><td>KEEP</td></tr>
<tr><td>Demo Middleware</td><td>Integration</td><td>99.7%</td><td>KEEP</td></tr>
<tr><td>Demo 3PL Tech</td><td>Fulfillment</td><td>98%</td><td class="warn">WATCH</td></tr>
</table>
</div>
</div>

<div class="two">
<div class="card">
<h2>International Readiness</h2>
<table>
<tr><th>Subsidiary</th><th>Currency</th><th>Control Focus</th></tr>
<tr><td>US</td><td>USD</td><td>Domestic commerce / retail</td></tr>
<tr><td>Canada</td><td>CAD</td><td>Currency / tax / fulfillment</td></tr>
<tr><td>EU</td><td>EUR</td><td>Regional reporting / consolidation</td></tr>
</table>
</div>
<div class="card">
<h2>30 / 60 / 90-Day Ownership Roadmap</h2>
<table>
<tr><td><b>Days 1–30</b></td><td>Discover systems, integrations, vendors, contracts, roles, data and risks</td></tr>
<tr><td><b>Days 31–60</b></td><td>Improve monitoring, governance, dashboards, workflows, vendor accountability and spend</td></tr>
<tr><td><b>Days 61–90</b></td><td>Publish roadmap, KPI cadence, automation priorities, support model and governance rhythm</td></tr>
</table>
</div>
</div>
</div>
<script>
document.getElementById("orderForm").addEventListener("submit", async e=>{
 e.preventDefault();
 const f=new FormData(e.target);
 const body={externalId:f.get("externalId"),customer:f.get("customer"),sku:f.get("sku"),quantity:Number(f.get("quantity"))};
 const r=await fetch("/api/orders",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
 const d=await r.json();
 document.getElementById("result").textContent=JSON.stringify(d,null,2);
 if(r.ok) setTimeout(()=>location.reload(),1100);
});
async function retryException(id){
 const r=await fetch(`/api/exceptions/${id}/retry`,{method:"POST"});
 const d=await r.json(); alert(JSON.stringify(d,null,2)); location.reload();
}
</script>
</body>
</html>
"""

def conn():
    c=sqlite3.connect(DB)
    c.row_factory=sqlite3.Row
    return c

def init_db():
    c=conn(); cur=c.cursor()
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS inventory(
      sku TEXT PRIMARY KEY, on_hand INTEGER, committed INTEGER, reorder_point INTEGER, preferred_stock INTEGER
    );
    CREATE TABLE IF NOT EXISTS orders(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      external_id TEXT UNIQUE, customer TEXT, sku TEXT, quantity INTEGER,
      amount REAL, sales_order TEXT, status TEXT, created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS fulfillment(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      sales_order TEXT, fulfillment_id TEXT, invoice_id TEXT, status TEXT, created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS exceptions(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      external_id TEXT, sku TEXT, quantity INTEGER, error_code TEXT,
      business_impact TEXT, status TEXT, created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS purchase_orders(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      sku TEXT, quantity INTEGER, po_number TEXT, status TEXT, created_at TEXT
    );
    CREATE TABLE IF NOT EXISTS logs(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      event_type TEXT, reference TEXT, status TEXT, message TEXT, created_at TEXT
    );
    """)
    for sku,v in ITEMS.items():
        cur.execute("INSERT OR IGNORE INTO inventory VALUES (?,?,?,?,?)",
                    (sku, 1200 if sku=="DEMO-WATER-FILTER" else 260 if sku=="DEMO-HOME-PITCHER" else 900,
                     250 if sku=="DEMO-WATER-FILTER" else 90 if sku=="DEMO-HOME-PITCHER" else 150,
                     v["reorder_point"], v["preferred_stock"]))
    c.commit(); c.close()

def log(event_type, reference, status, message=""):
    c=conn(); c.execute("INSERT INTO logs(event_type,reference,status,message,created_at) VALUES (?,?,?,?,?)",
                        (event_type,reference,status,message,datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    c.commit(); c.close()

def create_po_if_needed(sku):
    c=conn()
    inv=c.execute("SELECT * FROM inventory WHERE sku=?",(sku,)).fetchone()
    available=inv["on_hand"]-inv["committed"]
    if available < inv["reorder_point"]:
        exists=c.execute("SELECT 1 FROM purchase_orders WHERE sku=? AND status='OPEN'",(sku,)).fetchone()
        if not exists:
            qty=inv["preferred_stock"]-available
            po=f"PO-DEMO-{int(time.time())%100000}"
            c.execute("INSERT INTO purchase_orders(sku,quantity,po_number,status,created_at) VALUES (?,?,?,?,?)",
                      (sku,qty,po,"OPEN",datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            c.commit()
            log("PROCUREMENT",po,"CREATED",f"Replenishment for {sku}, qty {qty}")
    c.close()

@app.route("/")
def home():
    init_db(); c=conn()
    orders=c.execute("SELECT external_id,sales_order,sku,quantity,status FROM orders ORDER BY id DESC LIMIT 8").fetchall()
    exc=c.execute("SELECT id,external_id,error_code,business_impact FROM exceptions WHERE status='OPEN' ORDER BY id DESC LIMIT 8").fetchall()
    ful=c.execute("SELECT sales_order,fulfillment_id,invoice_id,status FROM fulfillment ORDER BY id DESC LIMIT 8").fetchall()
    logs=c.execute("SELECT created_at,event_type,reference,status FROM logs ORDER BY id DESC LIMIT 10").fetchall()
    inv_rows=c.execute("SELECT sku,(on_hand-committed) AS available,reorder_point FROM inventory").fetchall()
    total=c.execute("SELECT COUNT(*) n FROM orders").fetchone()["n"]
    fulfilled=c.execute("SELECT COUNT(*) n FROM fulfillment WHERE status='INVOICED'").fetchone()["n"]
    open_exc=c.execute("SELECT COUNT(*) n FROM exceptions WHERE status='OPEN'").fetchone()["n"]
    denom=total+open_exc
    success=round((total/denom)*100,1) if denom else 100.0
    c.close()
    return render_template_string(HTML, orders=orders, exceptions=exc, fulfillment=ful, logs=logs, inventory=inv_rows,
                                  k={"orders":total,"fulfilled":fulfilled,"exceptions":open_exc,"success":success})

@app.route("/api/orders",methods=["POST"])
def create_order():
    init_db()
    p=request.get_json(force=True)
    ext=(p.get("externalId") or "").strip()
    cust=(p.get("customer") or "").strip()
    sku=(p.get("sku") or "").strip()
    qty=int(p.get("quantity") or 0)

    if not ext or not cust or qty<=0:
        return jsonify({"status":"error","message":"externalId, customer, and positive quantity are required"}),400

    c=conn()
    if c.execute("SELECT 1 FROM orders WHERE external_id=?",(ext,)).fetchone():
        c.close()
        return jsonify({"status":"error","error":"DUPLICATE_ORDER","message":"External order already exists"}),409

    if sku not in ITEMS:
        c.execute("""INSERT INTO exceptions(external_id,sku,quantity,error_code,business_impact,status,created_at)
                     VALUES (?,?,?,?,?,'OPEN',?)""",
                  (ext,sku,qty,"SKU_NOT_FOUND","Fulfillment blocked; item cannot be allocated or invoiced.",
                   datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        c.commit(); c.close()
        log("VALIDATION",ext,"FAILED","SKU_NOT_FOUND")
        return jsonify({
            "status":"hold","error":"SKU_NOT_FOUND","externalId":ext,
            "businessImpact":"Fulfillment blocked; item cannot be allocated or invoiced.",
            "recommendedAction":"Correct SKU mapping and retry exception."
        }),422

    inv=c.execute("SELECT * FROM inventory WHERE sku=?",(sku,)).fetchone()
    available=inv["on_hand"]-inv["committed"]
    if available < qty:
        c.execute("""INSERT INTO exceptions(external_id,sku,quantity,error_code,business_impact,status,created_at)
                     VALUES (?,?,?,?,?,'OPEN',?)""",
                  (ext,sku,qty,"INSUFFICIENT_INVENTORY","Order cannot be fully allocated to the 3PL.",
                   datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        c.commit(); c.close()
        log("INVENTORY",ext,"FAILED","INSUFFICIENT_INVENTORY")
        return jsonify({"status":"hold","error":"INSUFFICIENT_INVENTORY","available":available}),422

    so=f"SO-DEMO-{int(time.time())%100000}"
    amount=round(ITEMS[sku]["price"]*qty,2)
    c.execute("""INSERT INTO orders(external_id,customer,sku,quantity,amount,sales_order,status,created_at)
                 VALUES (?,?,?,?,?,?,?,?)""",
              (ext,cust,sku,qty,amount,so,"PENDING_FULFILLMENT",datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    c.execute("UPDATE inventory SET committed=committed+? WHERE sku=?",(qty,sku))
    c.commit()
    log("SALES_ORDER",so,"CREATED",f"External order {ext}")
    # Simulate 3PL and invoicing
    fid=f"IF-DEMO-{int(time.time()*10)%100000}"
    inv_id=f"INV-DEMO-{int(time.time()*100)%100000}"
    c.execute("""INSERT INTO fulfillment(sales_order,fulfillment_id,invoice_id,status,created_at)
                 VALUES (?,?,?,?,?)""",(so,fid,inv_id,"INVOICED",datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    c.execute("UPDATE orders SET status='INVOICED' WHERE sales_order=?",(so,))
    c.execute("UPDATE inventory SET on_hand=on_hand-?, committed=committed-? WHERE sku=?",(qty,qty,sku))
    c.commit(); c.close()
    log("3PL_FULFILLMENT",fid,"SHIPPED",so)
    log("INVOICE",inv_id,"CREATED",so)
    create_po_if_needed(sku)

    return jsonify({
        "status":"success",
        "netSuiteProjection":{
            "customerRecord":cust,
            "salesOrder":so,
            "item":sku,
            "quantity":qty,
            "amount":amount,
            "orderStatus":"Invoiced"
        },
        "fulfillment":{"itemFulfillment":fid,"status":"Shipped"},
        "finance":{"invoice":inv_id,"status":"Created"}
    }),201

@app.route("/api/exceptions/<int:exc_id>/retry",methods=["POST"])
def retry_exception(exc_id):
    init_db(); c=conn()
    e=c.execute("SELECT * FROM exceptions WHERE id=?",(exc_id,)).fetchone()
    if not e:
        c.close(); return jsonify({"status":"error","message":"Exception not found"}),404
    if e["status"]!="OPEN":
        c.close(); return jsonify({"status":"error","message":"Exception already resolved"}),409

    # Demonstration recovery: map invalid SKU to valid demo SKU.
    corrected_sku="DEMO-WATER-FILTER"
    ext=e["external_id"]
    qty=e["quantity"]
    c.execute("UPDATE exceptions SET status='RESOLVED', sku=? WHERE id=?",(corrected_sku,exc_id))
    c.commit(); c.close()
    log("EXCEPTION_RECOVERY",ext,"RESOLVED",f"Corrected mapping to {corrected_sku}")
    return jsonify({
        "status":"resolved",
        "exceptionId":exc_id,
        "externalId":ext,
        "correctedSku":corrected_sku,
        "message":"Exception corrected and marked ready for controlled resubmission."
    })

@app.route("/api/health")
def health():
    init_db()
    return jsonify({"status":"ok","service":"business-systems-demo","database":"sqlite"})

if __name__=="__main__":
    init_db()
    app.run(host="127.0.0.1",port=8000,debug=True)
