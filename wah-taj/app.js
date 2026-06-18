/* ============================================================
   WAH! TAJ — app.js
   ============================================================ */
(function(){
"use strict";
var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
var $  = function(s,c){return (c||document).querySelector(s);};
var $$ = function(s,c){return Array.prototype.slice.call((c||document).querySelectorAll(s));};

/* reveal-on-scroll observer (hoisted so renderers can call it) */
var _revealIO = (reduce || !("IntersectionObserver" in window)) ? null :
  new IntersectionObserver(function(es){
    es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add("in"); _revealIO.unobserve(e.target); }});
  },{threshold:.14, rootMargin:"0px 0px -6% 0px"});
function observeReveals(){
  if(!_revealIO){ $$(".reveal").forEach(function(el){el.classList.add("in");}); return; }
  $$(".reveal:not(.in)").forEach(function(el){ _revealIO.observe(el); });
}

/* image helpers — real photos in images/<slug>.jpg, elegant gold fallback if missing */
function esc(s){return String(s).replace(/&/g,"&amp;").replace(/"/g,"&quot;").replace(/</g,"&lt;");}
function slugify(s){return String(s).toLowerCase().replace(/&/g,"and").replace(/[^a-z0-9]+/g,"-").replace(/(^-|-$)/g,"");}
function photoEl(slug, name, cls){
  return '<div class="photo'+(cls?" "+cls:"")+'" data-name="'+esc(name)+'">'+
    '<img src="images/'+slug+'.jpg" alt="'+esc(name)+'" loading="lazy" onerror="this.remove()"></div>';
}

/* ============================================================
   MENU DATA (full menu)
   ============================================================ */
var MENU = [
  {cat:"Appetizers", items:[
    {n:"Chicken Pakora", p:"9.99", d:"Tender chicken pieces enveloped in a chickpea batter, lightly spiced."},
    {n:"Vegetable Samosa", p:"5.99", d:"Crispy turnovers filled with savory potatoes and peas, seasoned with traditional Indian spices.", veg:true, pop:true},
    {n:"Spring Roll", p:"5.99", d:"Crispy, freshly-made rolls filled with seasonal vegetables and a dipping sauce.", veg:true},
    {n:"Mirchi Pakoda", p:"6.99", d:"Green chili peppers filled with spicy potato, coated in chickpea batter, deep-fried.", veg:true}
  ]},
  {cat:"Over Rice Bowls", items:[
    {n:"Chicken 65 Bowl", p:"12.99", d:"Marinated boneless chicken fried to perfection, with added gravy served over rice.", pop:true},
    {n:"Chili Chicken Bowl", p:"12.99", d:"Indo-Chinese chili chicken over basmati rice with a spicy glaze and fresh herbs."},
    {n:"Butter Chicken Bowl", p:"12.99", d:"Creamy tomato-based curry with tender chicken and aromatic spices, over rice.", pop:true},
    {n:"Chicken Tikka Masala Bowl", p:"12.99", d:"Oven-roasted tandoori chicken in a creamy tomato sauce, served over rice."},
    {n:"Mutton Masala Bowl", p:"13.99", d:"Goat masala over basmati rice with a savory spice blend and tomato sauce."},
    {n:"Veg Bowl", p:"11.99", d:"Aromatic basmati rice topped with a medley of seasoned vegetables.", veg:true},
    {n:"Chicken and Vegetable Bowl", p:"14.99", d:"Chicken and seasonal vegetables served over a bed of rice."}
  ]},
  {cat:"Kabab Rolls", items:[
    {n:"Beef Bihari Roll", p:"13.99", d:"Bihari-spiced sliced beef in paratha with onions, cilantro, and tamarind chutney."},
    {n:"Shami Roll", p:"13.99", d:"Minced meat, lentil & spice shami kabab rolled in naan with onions and tangy sauce."},
    {n:"Tandoori Tikka Boti Roll", p:"12.99", d:"Tandoor-grilled tikka boti in paratha with onions, cilantro, tamarind & yogurt sauce."},
    {n:"Chicken Malai Boti Roll", p:"12.99", d:"Creamy-marinated grilled chicken boti in paratha with onions and tamarind chutney."},
    {n:"Seekh Kabab Roll", p:"12.99", d:"Herbed seekh kabab grilled on skewers, wrapped with onions and green yogurt sauce."},
    {n:"Chicken 65 Roll", p:"12.99", d:"Chicken 65 in flatbread with fresh greens, onions, and a hint of tamarind chutney."},
    {n:"Chili Chicken Roll", p:"12.99", d:"Spiced chili chicken in paratha with lettuce, green peppers, and a zesty sauce."},
    {n:"Frankie Roll", p:"12.99", d:"Spiced vegetables (and meat) in soft paratha with onions, peppers, and Frankie sauce."},
    {n:"Bun Kabab", p:"10.99", d:"Ground kabab in a soft bun with egg and a blend of spices."}
  ]},
  {cat:"Vegetarian", items:[
    {n:"Navratan Korma", p:"14.99", d:"Mixed vegetables and paneer in a mildly sweet, creamy korma.", veg:true},
    {n:"Palak Paneer", p:"14.99", d:"Soft paneer simmered in a smooth spiced spinach gravy.", veg:true, pop:true},
    {n:"Paneer Tikka Masala", p:"14.99", d:"Grilled paneer in a creamy spiced tomato masala.", veg:true},
    {n:"Daal Tarka", p:"11.99", d:"Yellow lentils tempered with garlic, cumin, and spices.", veg:true},
    {n:"Bhindi Masala", p:"14.99", d:"Okra sauteed with onions, tomatoes, and aromatic spices.", veg:true},
    {n:"Khatti Daal", p:"11.99", d:"Tangy South-Asian style lentils with a bright, spiced finish.", veg:true}
  ]},
  {cat:"Chicken Curries", items:[
    {n:"Chicken Vindaloo Curry", p:"17.99", d:"Bold, flavorful curry with tangy vinegar and hot chilies."},
    {n:"Karahi Chicken Curry", p:"17.99", d:"Sauteed with onions, peppers & tomatoes, simmered with ginger, garlic and spices in a karahi."},
    {n:"Butter Chicken Curry", p:"17.99", d:"Creamy tomato-based curry with tender chicken and aromatic spices.", pop:true},
    {n:"Chicken Afghani Curry", p:"17.99", d:"Smoky grilled chicken simmered in a creamy sauce with garlic and ginger."},
    {n:"Chicken 65 Curry", p:"17.99", d:"Spicy marinated boneless chicken, fried to perfection."},
    {n:"Nawabi Chicken Curry", p:"17.99", d:"Rich, royal-style chicken curry with a luxurious spice blend."},
    {n:"Chilli Chicken Curry", p:"17.99", d:"Boneless chicken stir-fried with peppers and onions in a spicy chilli sauce."},
    {n:"Chicken Achaari Curry", p:"17.99", d:"Chicken cooked in a pickled (achaari) sauce with spices and herbs."},
    {n:"Chicken 65 Dry", p:"19.99", d:"Spicy, crisp boneless chicken 65 served dry."}
  ]},
  {cat:"Mutton Curries", items:[
    {n:"Karahi Gosht Curry", p:"21.99", d:"Tender goat cooked in a karahi with onions, tomatoes, ginger, garlic and spices."},
    {n:"Mutton Masala Curry", p:"21.99", d:"Mutton in a rich gravy of onions, tomatoes, and traditional spices."},
    {n:"Beef Nihari Curry", p:"19.99", d:"Slow-cooked beef shank in spices and herbs, garnished with ginger and cilantro."},
    {n:"Seekh Fry Curry", p:"19.99", d:"Minced mutton skewers with onions, herbs, and spices, fried to perfection."},
    {n:"Talawa Gosht Curry", p:"21.99", d:"Fried goat in a deeply spiced, savory gravy."}
  ]},
  {cat:"Platters", items:[
    {n:"Wah! Taj Platter", p:"32.99", d:"Chicken tikka, tandoori chicken, seekh kabob, skewer beef bihari, and chicken malai boti.", pop:true},
    {n:"Junior Platter", p:"19.99", d:"1 pc chicken tikka, 1 skewer seekh kabob, and 4-5 pieces chicken malai boti."}
  ]},
  {cat:"Grilled Items", items:[
    {n:"8 Pieces Tandoori Boti", p:"16.99", d:"Chicken marinated in yogurt and Indian spices, cooked in a tandoor oven."},
    {n:"2 Pieces Chicken Tikka", p:"17.99", d:"Chicken legs marinated in yogurt and spices, grilled for a smoky flavor."},
    {n:"4 Pieces Fish Fry", p:"16.99", d:"Fish fillets marinated in traditional spices, deep-fried to a golden crust."},
    {n:"8 Pieces Chicken Malai Boti", p:"19.99", d:"Boneless chicken in a creamy yogurt, cheese & mild spice marinade, grilled."},
    {n:"6 Pieces Goat Chops", p:"23.99", d:"Tender goat chops marinated in traditional spices and expertly grilled."},
    {n:"4 Pieces Beef Seekh Kabab", p:"16.99", d:"Minced beef with onions, herbs & spices, skewered and grilled."},
    {n:"4 Pieces Chicken Seekh Kabab", p:"16.99", d:"Minced chicken with traditional spices, skewered and grilled."},
    {n:"2 Pieces Chapli Kabab", p:"17.99", d:"Minced meat patties with spices, onions & tomatoes, cooked on a grill."}
  ]},
  {cat:"Rice", items:[
    {n:"Plain Rice", p:"6.99", d:"Simply steamed, fluffy white rice - the perfect accompaniment.", veg:true},
    {n:"Zeera Rice", p:"9.99", d:"Basmati rice sauteed with cumin seeds and a hint of clarified butter.", veg:true},
    {n:"Peas Pulao", p:"11.99", d:"Basmati rice and green peas cooked with whole spices and herbs.", veg:true},
    {n:"Veg Fried Rice", p:"13.99", d:"Mixed vegetables stir-fried with rice.", veg:true},
    {n:"Chicken Fried Rice", p:"15.99", d:"Classic chicken fried rice with tender chicken, veggies, and seasoned rice."},
    {n:"Goat Pulao", p:"17.99", d:"Basmati rice and goat cooked with a blend of spices and aromatic herbs."},
    {n:"Chicken Biryani", p:"16.99", d:"Aromatic basmati layered with spiced chicken, fried onions, and herbs.", pop:true},
    {n:"Mutton Biryani", p:"21.99", d:"Basmati and tender mutton with yogurt, spices, fried onions, and coriander."}
  ]},
  {cat:"Breads", items:[
    {n:"Plain Naan", p:"3.99", d:"Soft, warm, fluffy traditional Indian flatbread.", veg:true},
    {n:"Plain Paratha", p:"4.49", d:"Flaky, buttery flatbread, a versatile accompaniment for curries.", veg:true},
    {n:"Lacha Paratha", p:"4.99", d:"Multi-layered whole wheat flatbread with butter, baked in a tandoor.", veg:true}
  ]},
  {cat:"Desserts", items:[
    {n:"Gulab Jamun", p:"4.99", d:"2 pieces. Fried milk-solid balls soaked in cardamom & rose syrup.", veg:true},
    {n:"Ras Malai", p:"5.99", d:"2 pieces. Cheese dumplings in sweet thickened milk with cardamom & pistachios.", veg:true},
    {n:"Gajar Halwa", p:"7.99", d:"Grated carrots cooked with milk, sugar, and aromatic spices.", veg:true},
    {n:"Moong Daal Halwa", p:"5.99", d:"Yellow moong lentils in ghee, sweetened and garnished with nuts.", veg:true},
    {n:"Fruit Custard", p:"7.99", d:"Fresh seasonal fruits in a creamy homemade vanilla custard.", veg:true}
  ]},
  {cat:"Drinks", items:[
    {n:"Avocado Shake", p:"8.99", d:"Ripe avocados blended with milk and a hint of sweetness.", veg:true},
    {n:"Mango Lassi", p:"7.99", d:"Traditional Indian drink with mango and yogurt.", veg:true, pop:true},
    {n:"Butter Milk Salted", p:"5.99", d:"Yogurt blended with water, salt, and roasted cumin.", veg:true}
  ]},
  {cat:"Kids", items:[
    {n:"Kids Chicken Nuggets", p:"8.99", d:"6 pieces. Battered, deep-fried chicken in a kid-sized portion."},
    {n:"Kids Fries", p:"5.99", d:"Crispy golden seasoned potato fries."}
  ]}
];

/* ============================================================
   FEATURED / SIGNATURE (with photos)
   ============================================================ */
var FEATURES = [
  {slug:"chicken-biryani", n:"Chicken Biryani", p:"16.99", d:"Aromatic basmati layered with spiced chicken, fried onions & herbs.", pop:true},
  {slug:"chicken-65", n:"Chicken 65", p:"12.99", d:"Marinated boneless chicken fried to perfection with a fiery kick.", pop:true},
  {slug:"butter-chicken", n:"Butter Chicken", p:"17.99", d:"Creamy tomato curry with tender chicken & aromatic spices.", pop:true},
  {slug:"mixed-grill-platter", n:"Wah! Taj Platter", p:"32.99", d:"Tikka, tandoori chicken, seekh kabob, beef bihari & malai boti.", pop:true},
  {slug:"palak-paneer", n:"Palak Paneer", p:"14.99", d:"Soft paneer in a smooth, spiced spinach gravy.", veg:true},
  {slug:"mango-lassi", n:"Mango Lassi", p:"7.99", d:"Cool, sweet mango blended with creamy yogurt.", pop:true}
];
(function renderFeatures(){
  var g = $("#featureGrid"); if(!g) return;
  g.innerHTML = FEATURES.map(function(f,i){
    return '<article class="feature reveal" data-d="'+(i%3)+'">'+
      '<div class="feature-photo">'+ photoEl(f.slug, f.n) + (f.pop?'<span class="fav-badge">Popular</span>':'') +'</div>'+
      '<div class="feature-body">'+
        '<h3>'+f.n+'</h3>'+
        '<p class="fdesc">'+f.d+'</p>'+
        '<div class="fprice">From <b>$'+f.p+'</b></div>'+
      '</div>'+
    '</article>';
  }).join("");
})();

/* ============================================================
   GALLERY (real photos)
   ============================================================ */
(function renderGallery(){
  var g = $("#galleryGrid"); if(!g) return;
  var TILES = [
    {slug:"chicken-biryani",    t:"Chicken Biryani",   s:"Signature",  cls:"big"},
    {slug:"butter-chicken",     t:"Butter Chicken",    s:"Curry"},
    {slug:"seekh-kabab",        t:"Seekh Kabab",       s:"From the Grill"},
    {slug:"mixed-grill-platter",t:"Wah! Taj Platter",  s:"Grill",      cls:"wide"},
    {slug:"chicken-65",         t:"Chicken 65",        s:"Fan Favorite"},
    {slug:"tandoori-chicken",   t:"Tandoori Boti",     s:"Tandoor"},
    {slug:"palak-paneer",       t:"Palak Paneer",      s:"Vegetarian"},
    {slug:"gulab-jamun",        t:"Gulab Jamun",       s:"Dessert"}
  ];
  g.innerHTML = TILES.map(function(t,i){
    return '<figure class="gtile reveal '+(t.cls||"")+'" data-d="'+(i%3)+'">'+
      photoEl(t.slug, t.t) +
      '<div class="veil"></div>'+
      '<figcaption class="gcap"><div class="gs">'+t.s+'</div><div class="gt">'+t.t+'</div></figcaption>'+
    '</figure>';
  }).join("");
})();

/* ============================================================
   MARQUEE
   ============================================================ */
(function(){
  var t = $("#marqueeTrack"); if(!t) return;
  var words = ["Chicken Biryani","Chicken 65","Butter Chicken","Wah! Taj Platter","Seekh Kabab","Mango Lassi","Nihari","Tandoori Boti","Paneer Tikka","Goat Chops"];
  var one = words.map(function(w){return '<span class="marquee-item">'+w+'</span>';}).join("");
  t.innerHTML = one + one;
})();

/* ============================================================
   MENU RENDER + FILTER + SEARCH
   ============================================================ */
(function(){
  var list = $("#menuList"), tabs = $("#menuTabs"), search = $("#menuSearch"), empty = $("#menuEmpty");
  if(!list) return;
  var cats = ["All"].concat(MENU.map(function(m){return m.cat;}));
  tabs.innerHTML = cats.map(function(c,i){
    return '<button class="menu-tab'+(i===0?' active':'')+'" role="tab" aria-selected="'+(i===0)+'" data-cat="'+c+'">'+c+'</button>';
  }).join("");

  function itemHTML(it){
    return '<div class="menu-item">'+
      '<div class="mi-thumb">'+ photoEl(slugify(it.n), it.n) +'</div>'+
      '<div class="mi-body">'+
        '<div class="mi-head"><span class="mi-name">'+
          (it.veg?'<span class="veg-dot" title="Vegetarian" aria-label="Vegetarian"></span>':'')+
          it.n + (it.pop?' <span class="pop-tag">Popular</span>':'')+
        '</span><span class="mi-price">$'+it.p+'</span></div>'+
        '<p class="mi-desc">'+it.d+'</p>'+
      '</div></div>';
  }

  function render(cat, q){
    cat = cat || "All"; q = (q||"").trim().toLowerCase();
    var html = "", shown = 0;
    MENU.forEach(function(group){
      if(cat!=="All" && group.cat!==cat) return;
      var items = group.items.filter(function(it){
        return !q || it.n.toLowerCase().indexOf(q)>-1 || it.d.toLowerCase().indexOf(q)>-1;
      });
      if(!items.length) return;
      shown += items.length;
      html += '<div class="menu-cat reveal"><h3 class="menu-cat-title">'+group.cat+'</h3>'+
        '<div class="menu-items">'+items.map(itemHTML).join("")+'</div></div>';
    });
    list.innerHTML = html;
    empty.hidden = shown>0;
    observeReveals();
  }

  tabs.addEventListener("click", function(e){
    var b = e.target.closest(".menu-tab"); if(!b) return;
    $$(".menu-tab", tabs).forEach(function(x){x.classList.remove("active");x.setAttribute("aria-selected","false");});
    b.classList.add("active"); b.setAttribute("aria-selected","true");
    render(b.dataset.cat, search.value);
  });
  var deb;
  search.addEventListener("input", function(){
    clearTimeout(deb);
    deb = setTimeout(function(){
      var active = $(".menu-tab.active", tabs);
      render(active?active.dataset.cat:"All", search.value);
    },140);
  });
  render("All","");
})();

/* ============================================================
   REVIEWS
   ============================================================ */
(function(){
  var bars = $("#ratingBars"), grid = $("#reviewGrid");
  var dist = [[5,82],[4,12],[3,3],[2,1],[1,2]];
  if(bars){
    bars.innerHTML = dist.map(function(d){
      return '<div class="rbar"><span>'+d[0]+'★</span><span class="track"><span class="fill" data-w="'+d[1]+'"></span></span></div>';
    }).join("");
  }
  var REVIEWS = [
    {name:"Blaze Quadri", meta:"3 months ago · Dine in", stars:5, featured:true,
     text:"Probably the best food I have eaten in my life after I came to the USA. Today I tried their buffet and it was the best — the chicken tikka was my favorite. I would 100% come back and recommend it to all of you too.", tag:"Food 5 · Service 5 · Atmosphere 5"},
    {name:"Phyllis Felts", meta:"Local Guide · a month ago", stars:5,
     text:"We were delighted with the food! The servings were ample and the price was decent. We ordered chicken skewers, mutter paneer, and garlic naan — together they made a very well-rounded meal.", tag:"Generous portions"},
    {name:"Ammaar Ansari", meta:"Local Guide · 3 weeks ago", stars:5,
     text:"The food was absolutely amazing and full of flavor. We got the biryani, nihari, grill platter, butter chicken, chai, and paan. Every dish came out fresh, hot, and well presented.", tag:"Fresh & flavorful"},
    {name:"Yasmin Infante", meta:"Local Guide · 8 months ago", stars:5,
     text:"Some of the most delicious Indian food I have ever eaten. The paneer literally melts in your mouth — perfect texture and moisture. Paneer Tikka Masala, Palak Paneer, Garlic Naan and rice were all fantastic.", tag:"Paneer perfection"}
  ];
  if(grid){
    grid.innerHTML = REVIEWS.map(function(r,i){
      var initials = r.name.split(" ").map(function(p){return p[0];}).join("").slice(0,2);
      return '<article class="review'+(r.featured?' featured':'')+' reveal" data-d="'+(i%3)+'">'+
        '<div class="rev-head"><span class="rev-av">'+initials+'</span>'+
          '<div><div class="rev-name">'+r.name+'</div><div class="rev-meta">'+r.meta+'</div></div></div>'+
        '<div class="rev-stars" aria-label="'+r.stars+' stars">'+ "★★★★★".slice(0,r.stars) +'</div>'+
        '<p class="rev-text">'+r.text+'</p>'+
        '<span class="rev-tag">'+r.tag+'</span>'+
      '</article>';
    }).join("");
  }
  // animate bars when in view
  var band = $(".rating-band");
  if(band){
    if(reduce || !("IntersectionObserver" in window)){
      $$(".fill", bars).forEach(function(f){f.style.width=f.dataset.w+"%";});
    } else {
      var io = new IntersectionObserver(function(es){
        es.forEach(function(e){ if(e.isIntersecting){ $$(".fill", bars).forEach(function(f){f.style.width=f.dataset.w+"%";}); io.disconnect(); }});
      },{threshold:.4});
      io.observe(band);
    }
  }
})();

/* ============================================================
   HERO — interactive "flavor network" canvas
   ============================================================ */
(function(){
  var canvas = $("#net"); if(!canvas) return;
  var ctx = canvas.getContext("2d");
  var w,h,dpr, nodes=[], mouse={x:-999,y:-999}, scrollY=0, raf;
  var COUNT;
  function size(){
    dpr = Math.min(window.devicePixelRatio||1, 2);
    w = canvas.clientWidth; h = canvas.clientHeight;
    canvas.width = w*dpr; canvas.height = h*dpr;
    ctx.setTransform(dpr,0,0,dpr,0,0);
    COUNT = Math.min(70, Math.floor(w*h/16000));
    init();
  }
  function init(){
    nodes = [];
    for(var i=0;i<COUNT;i++){
      nodes.push({x:Math.random()*w, y:Math.random()*h, vx:(Math.random()-.5)*.25, vy:(Math.random()-.5)*.25, r:Math.random()*1.6+1});
    }
  }
  function step(){
    ctx.clearRect(0,0,w,h);
    var par = scrollY*0.04;
    for(var i=0;i<nodes.length;i++){
      var n=nodes[i];
      n.x+=n.vx; n.y+=n.vy;
      if(n.x<0||n.x>w)n.vx*=-1;
      if(n.y<0||n.y>h)n.vy*=-1;
      // mouse attraction
      var mdx=mouse.x-n.x, mdy=mouse.y-n.y, md=Math.sqrt(mdx*mdx+mdy*mdy);
      if(md<160){ n.x+=mdx/md*0.6; n.y+=mdy/md*0.6; }
      var py=n.y - par;
      ctx.beginPath();
      ctx.arc(n.x, py, n.r, 0, Math.PI*2);
      ctx.fillStyle="rgba(212,175,55,.85)";
      ctx.fill();
      for(var j=i+1;j<nodes.length;j++){
        var m=nodes[j], dx=n.x-m.x, dy=n.y-m.y, dist=Math.sqrt(dx*dx+dy*dy);
        if(dist<130){
          var a=(1-dist/130)*.45;
          var grd=ctx.createLinearGradient(n.x,py,m.x,m.y-par);
          grd.addColorStop(0,"rgba(236,213,137,"+a+")");
          grd.addColorStop(1,"rgba(164,126,34,"+a+")");
          ctx.strokeStyle=grd; ctx.lineWidth=.7;
          ctx.beginPath(); ctx.moveTo(n.x,py); ctx.lineTo(m.x,m.y-par); ctx.stroke();
        }
      }
    }
    raf=requestAnimationFrame(step);
  }
  function staticFrame(){
    init(); ctx.clearRect(0,0,w,h);
    nodes.forEach(function(n){ctx.beginPath();ctx.arc(n.x,n.y,n.r,0,Math.PI*2);ctx.fillStyle="rgba(212,175,55,.5)";ctx.fill();});
  }
  window.addEventListener("resize", size, {passive:true});
  window.addEventListener("mousemove", function(e){
    var r=canvas.getBoundingClientRect(); mouse.x=e.clientX-r.left; mouse.y=e.clientY-r.top;
  }, {passive:true});
  window.addEventListener("mouseout", function(){mouse.x=mouse.y=-999;});
  window.addEventListener("scroll", function(){ scrollY = window.scrollY; }, {passive:true});
  size();
  if(reduce){ staticFrame(); } else { step(); }
})();

/* ============================================================
   HERO — spice DNA helix ("DNA of flavor")
   ============================================================ */
(function(){
  var helix = $("#helix"); if(!helix) return;
  var N = 26, colors=["#f6e6a8","#d4af37","#a47e22","#ecd589"];
  var html="";
  for(var i=0;i<N;i++){
    var t=i/N;
    html+='<i class="dna" data-i="'+i+'" style="--t:'+t+';--col:'+colors[i%4]+'"></i>';
    html+='<i class="dna dna2" data-i="'+i+'" style="--t:'+t+';--col:'+colors[(i+2)%4]+'"></i>';
  }
  helix.innerHTML = html;
  // styling injected here to keep CSS file focused
  var s=document.createElement("style");
  s.textContent=
   ".helix{position:absolute}.dna{position:absolute;left:50%;width:13px;height:13px;border-radius:50%;"+
   "background:var(--col);box-shadow:0 0 12px var(--col);transform:translateX(calc(sin(var(--ang)) * 90px));"+
   "top:calc(var(--t) * 100%);opacity:calc(.4 + (cos(var(--ang)) + 1) * .3);}"+
   ".dna{--ang:calc((var(--t) * 6.5 + var(--spin,0)) * 1rad)}";
  document.head.appendChild(s);
  var dots=$$(".dna",helix);
  var spin=0;
  function tick(){
    spin+=0.012;
    dots.forEach(function(d){
      var t=parseFloat(d.style.getPropertyValue("--t"));
      var phase=(d.classList.contains("dna2"))?Math.PI:0;
      var ang=t*6.5 + spin + phase;
      var x=Math.sin(ang)*90, sc=(Math.cos(ang)+1)/2;
      d.style.transform="translateX("+x+"px) scale("+(0.6+sc*0.7)+")";
      d.style.opacity=(0.35+sc*0.6).toFixed(2);
      d.style.zIndex=Math.round(sc*10);
    });
    raf=requestAnimationFrame(tick);
  }
  var raf;
  // react to scroll: shift helix vertically + speed
  window.addEventListener("scroll", function(){
    helix.style.transform="translateY(calc(-50% + "+(window.scrollY*0.06)+"px))";
  }, {passive:true});
  if(!reduce) tick(); else dots.forEach(function(d){var t=parseFloat(d.style.getPropertyValue("--t"));var ang=t*6.5+(d.classList.contains("dna2")?Math.PI:0);d.style.transform="translateX("+Math.sin(ang)*90+"px)";});
})();

/* ============================================================
   HERO dish tilt on pointer
   ============================================================ */
(function(){
  if(reduce || window.matchMedia("(hover: none)").matches) return;
  var stage=$("#heroStage"); if(!stage) return;
  var card=$(".tilt",stage); if(!card) return;
  stage.addEventListener("pointermove",function(e){
    var r=stage.getBoundingClientRect();
    var x=(e.clientX-r.left)/r.width-.5, y=(e.clientY-r.top)/r.height-.5;
    card.style.transform="rotateY("+(x*12)+"deg) rotateX("+(-y*12)+"deg) translateZ(10px)";
  });
  stage.addEventListener("pointerleave",function(){card.style.transform="";});
})();

/* ============================================================
   EXPLODED VIEW — scroll-driven layer separation
   ============================================================ */
(function(){
  var section=$("#exploded"), track=$(".exploded-track",section), layers=$$(".layer",section), bar=$("#explodedBar");
  if(!section||!layers.length) return;
  var stackGap=10;   // collapsed spacing
  var maxSpread=66;  // exploded spacing
  function update(){
    var rect=track.getBoundingClientRect();
    var total=track.offsetHeight - window.innerHeight;
    var prog=Math.min(1, Math.max(0, -rect.top/total));
    // ease the spread in the middle of the scroll
    var spread = stackGap + (maxSpread-stackGap)*prog;
    var mid=(layers.length-1)/2;
    layers.forEach(function(l,i){
      var y=(i-mid)*spread;
      var rot=62 - prog*6;
      l.style.transform="translateY("+y+"px) rotateX("+rot+"deg) scale("+(1-Math.abs(i-mid)*0.01)+")";
      l.style.zIndex=String(layers.length-i);
    });
    if(bar) bar.style.width=(prog*100).toFixed(1)+"%";
    section.classList.toggle("lit", prog>0.12);
  }
  if(reduce){
    var mid=(layers.length-1)/2;
    layers.forEach(function(l,i){l.style.transform="translateY("+((i-mid)*maxSpread)+"px) rotateX(56deg)";});
    section.classList.add("lit"); if(bar)bar.style.width="100%";
    return;
  }
  var ticking=false;
  window.addEventListener("scroll",function(){
    if(!ticking){requestAnimationFrame(function(){update();ticking=false;});ticking=true;}
  },{passive:true});
  window.addEventListener("resize",update,{passive:true});
  update();
})();

/* ============================================================
   NAV scroll state + mobile menu + status
   ============================================================ */
(function(){
  var nav=$("#nav"), links=$("#navLinks"), burger=$("#burger");
  function onScroll(){ nav.classList.toggle("scrolled", window.scrollY>30); }
  window.addEventListener("scroll", onScroll, {passive:true}); onScroll();
  if(burger){
    burger.addEventListener("click", function(){
      var open=links.classList.toggle("open"); nav.classList.toggle("open", open);
      burger.setAttribute("aria-expanded", open);
    });
    links.addEventListener("click", function(e){
      if(e.target.tagName==="A"){ links.classList.remove("open"); nav.classList.remove("open"); burger.setAttribute("aria-expanded", false); }
    });
  }
  // open/closed status (opens 11:30, assume close 22:00 local)
  var chip=$("#statusChip"), txt=$("#statusText"), hours=$("#hoursLine");
  var now=new Date(), hr=now.getHours()+now.getMinutes()/60;
  var open = hr>=11.5 && hr<22;
  if(chip&&open){ chip.classList.add("open"); txt.textContent="Open now · until 10 PM"; if(hours)hours.innerHTML="Open now · until 10:00 PM<br><span>Open daily 11:30 AM – 10:00 PM</span>"; }
})();

/* reveal: observe any remaining static .reveal elements */
observeReveals();

/* ============================================================
   COUNT-UP (rating + reviews)
   ============================================================ */
(function(){
  var els=$$("[data-count]");
  function run(el){
    var target=parseFloat(el.dataset.count), dec=parseInt(el.dataset.decimals||"0",10), dur=1400, t0=null;
    if(reduce){ el.textContent= dec? target.toFixed(dec): Math.round(target).toLocaleString("en-US"); return; }
    function fr(ts){
      if(!t0)t0=ts; var p=Math.min((ts-t0)/dur,1), e=1-Math.pow(1-p,3), v=target*e;
      el.textContent = dec? v.toFixed(dec) : Math.round(v).toLocaleString("en-US");
      if(p<1)requestAnimationFrame(fr);
    }
    requestAnimationFrame(fr);
  }
  if(!("IntersectionObserver" in window)){ els.forEach(run); return; }
  var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){run(e.target);io.unobserve(e.target);}});},{threshold:.6});
  els.forEach(function(el){io.observe(el);});
})();

/* ============================================================
   RESERVATION FORM validation
   ============================================================ */
(function(){
  var form=$("#resForm"); if(!form) return;
  var ok=$("#resSuccess");
  function check(field){
    var input=field.querySelector("input,select"); if(!input) return true;
    var valid=true;
    if(input.required && !input.value.trim()) valid=false;
    if(input.type==="tel" && input.value && input.value.replace(/\D/g,"").length<7) valid=false;
    field.classList.toggle("invalid", !valid);
    return valid;
  }
  $$(".field input,.field select", form).forEach(function(i){
    i.addEventListener("blur", function(){ check(i.closest(".field")); });
  });
  form.addEventListener("submit", function(e){
    e.preventDefault();
    var fields=$$(".field", form), allOk=true, firstBad=null;
    fields.forEach(function(f){ if(!check(f)){ allOk=false; if(!firstBad)firstBad=f; }});
    if(!allOk){ if(firstBad){var inp=firstBad.querySelector("input,select"); if(inp)inp.focus();} return; }
    ok.classList.add("show"); ok.scrollIntoView({behavior:reduce?"auto":"smooth", block:"center"});
    form.querySelectorAll("input").forEach(function(i){ if(i.type!=="time"&&i.type!=="date") i.value=""; });
    setTimeout(function(){ ok.classList.remove("show"); }, 6000);
  });
  // default date = today
  var d=$("#rdate"); if(d){ d.value=new Date().toISOString().slice(0,10); }
})();

})();
