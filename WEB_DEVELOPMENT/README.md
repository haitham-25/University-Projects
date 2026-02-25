# AutoDrive - Car Listing & Test Drive Booking Website

A comprehensive, multi-page car listing website with modern design, advanced features, and full functionality.

## 🚀 Features

### Core Functionality
- ✅ **User Registration & Login System**
- ✅ **Browse Car Listings** with advanced filters
- ✅ **Car Search & Filters** (make, model, price, body type, fuel type)
- ✅ **Compare Cars** side-by-side (up to 3 vehicles)
- ✅ **Download Brochures** functionality
- ✅ **Test Drive Booking** system
- ✅ **View Dealerships** with locations and ratings
- ✅ **Car Loan Calculator** with interactive sliders
- ✅ **Price Updates** in real-time
- ✅ **Contact Dealerships** feature
- ✅ **User Dashboard** with saved cars and activity
- ✅ **Dealer Dashboard** with analytics
- ✅ **Review & Rating System**
- ✅ **Car Insurance Information**
- ✅ **Car Maintenance Guide**
- ✅ **Upcoming Car Models**
- ✅ **Blog & Articles** section
- ✅ **FAQ Section** with interactive Q&A
- ✅ **Admin Panel** interface ready

## 📁 File Structure

```
car-website/
│
├── index.html                 # Home page
│
├── css/
│   └── style.css             # Main stylesheet (shared across all pages)
│
├── js/
│   ├── main.js               # Core JavaScript functionality
│   └── cars.js               # Car inventory data
│
├── pages/
│   ├── browse.html           # Browse cars with filters
│   ├── calculator.html       # Loan calculator
│   ├── dealerships.html      # Dealership listings
│   ├── contact.html          # Contact form
│   ├── blog.html             # Blog & articles
│   └── faq.html              # FAQ page
│
└── README.md                 # This file
```

## 🎨 Design Features

- **Modern Automotive Aesthetic**: Bold orange/red gradient theme inspired by performance cars
- **Custom Fonts**: Orbitron (headings) + Archivo (body text)
- **Smooth Animations**: Fade-ins, slide-ins, hover effects
- **Fully Responsive**: Works on desktop, tablet, and mobile
- **Dark Theme**: Eye-friendly dark color scheme
- **Interactive Elements**: Modals, sliders, dynamic content

## 💻 Pages Overview

### 1. Home Page (index.html)
- Hero section with search bar
- Key statistics
- Feature highlights
- Call-to-action sections

### 2. Browse Cars (pages/browse.html)
- Advanced filter sidebar (price, body type, fuel, year)
- Car grid with 15+ vehicles
- Save to favorites functionality
- Test drive booking
- Sorting options

### 3. Loan Calculator (pages/calculator.html)
- Interactive sliders for vehicle price, down payment, interest rate
- Real-time calculation
- Detailed breakdown (monthly payment, total interest, total cost)
- Financial tips section

### 4. Dealerships (pages/dealerships.html)
- 6+ dealership locations
- Ratings and reviews
- Business hours
- Contact information

### 5. Contact (pages/contact.html)
- Contact form with validation
- Business information
- Social media links
- Multiple contact methods

### 6. Blog & Articles (pages/blog.html)
- 6+ article previews
- Categories: Reviews, Tips, Industry News
- Engaging visual design

### 7. FAQ (pages/faq.html)
- Interactive accordion-style Q&A
- 8+ common questions
- Expandable/collapsible answers

## 🔧 Technical Features

### JavaScript Functionality
- **Authentication System**: Login/Register with localStorage
- **Local Storage Management**: Saves user data, preferences, saved cars
- **Modal System**: Reusable modals for login, register, test drives
- **Form Validation**: Client-side validation for all forms
- **Dynamic Content**: Car cards generated from data
- **Smooth Scrolling**: Enhanced navigation experience
- **Mobile Menu**: Responsive navigation for mobile devices

### CSS Features
- **CSS Variables**: Consistent theming across all pages
- **Grid & Flexbox**: Modern layout techniques
- **Animations**: Keyframe animations for visual appeal
- **Transitions**: Smooth state changes
- **Media Queries**: Responsive breakpoints

## 🚀 How to Use

### For Users:
1. Open `index.html` in a web browser
2. Browse cars, use filters, save favorites
3. Book test drives
4. Use the loan calculator
5. Read blog articles and FAQ

### For Developers:
1. All pages are linked and fully functional
2. Modify `style.css` for design changes
3. Update `cars.js` to add/modify car inventory
4. Customize `main.js` for functionality changes
5. Each page is independent but shares common assets

## 📱 Responsive Design

The website is fully responsive with breakpoints at:
- Desktop: 1400px+
- Laptop: 1024px - 1399px
- Tablet: 768px - 1023px
- Mobile: < 768px

## 🎯 Key JavaScript Functions

### Authentication
- `Auth.login(userData)` - Log in user
- `Auth.logout()` - Log out user
- `Auth.isLoggedIn()` - Check login status

### Car Management
- `SavedCars.save(car)` - Save car to favorites
- `SavedCars.remove(carId)` - Remove from favorites
- `SavedCars.isSaved(carId)` - Check if car is saved

### Test Drives
- `TestDrives.book(booking)` - Book a test drive
- `TestDrives.getBookings()` - Get all bookings

### Comparison
- `Comparison.add(car)` - Add car to comparison (max 3)
- `Comparison.remove(carId)` - Remove from comparison

### Utilities
- `formatCurrency(amount)` - Format numbers as USD
- `showSuccessMessage(message)` - Display success notification

## 🎨 Color Scheme

```css
--primary: #FF3D00      /* Main orange/red */
--secondary: #1A1A1A    /* Dark gray */
--accent: #FFD600       /* Yellow accent */
--dark: #0A0A0A         /* Deep black */
--light: #F5F5F5        /* Off-white */
--text: #E0E0E0         /* Light gray text */
```

## 📊 Sample Data

The website includes:
- **15 cars** in the inventory (Tesla, BMW, Porsche, Ford, Mercedes, Toyota, etc.)
- **6 dealerships** with full details
- **6 blog articles** with engaging topics
- **8 FAQ items** covering common questions

## 🔮 Future Enhancements

Potential additions:
- Backend integration (Node.js/PHP)
- Database connection (MySQL/MongoDB)
- Payment gateway integration
- Real-time chat support
- Email notifications
- Advanced search with AI
- Virtual showroom (360° views)
- Credit score checker
- Insurance quotes API

## 📄 License

This is a demonstration project created for educational purposes.

## 🤝 Support

For questions or issues:
- Email: info@autodrive.com
- Phone: 1-800-AUTO-DRIVE

---

**Built with HTML, CSS, and JavaScript**
**No frameworks or dependencies required**
**Just open index.html and start exploring!**
