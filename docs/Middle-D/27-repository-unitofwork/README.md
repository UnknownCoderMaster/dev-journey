# Repository Pattern, Unit of Work Pattern — Middle D

## 1. Nima? (Ta'rif)

**Repository** — ma'lumotlar bazasi bilan ishlash logikasini
**abstraksiya** ortiga yashiruvchi pattern. **Unit of Work** — bir
nechta Repository operatsiyasini **bitta transaction** sifatida
birlashtiruvchi pattern.

## 2. Nima uchun kerak?

Controller/Service ichida to'g'ridan `DbContext`/SQL kodi yozilsa —
biznes mantiq va ma'lumotlar bazasi logikasi **aralashib ketadi**,
test qilish qiyinlashadi (haqiqiy DB kerak bo'ladi). Repository —
bu ikkalasini **ajratadi**.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Generic Repository vs Specific Repository

```csharp
// Generic — barcha entity uchun UMUMIY CRUD
public interface IRepository<T> where T : class
{
    Task<T?> GetByIdAsync(int id);
    Task<List<T>> GetAllAsync();
    Task AddAsync(T entity);
    void Update(T entity);
    void Delete(T entity);
}

public class Repository<T> : IRepository<T> where T : class
{
    private readonly AppDbContext _context;
    private readonly DbSet<T> _dbSet;

    public Repository(AppDbContext context)
    {
        _context = context;
        _dbSet = context.Set<T>();
    }

    public async Task<T?> GetByIdAsync(int id) => await _dbSet.FindAsync(id);
    public async Task<List<T>> GetAllAsync() => await _dbSet.ToListAsync();
    public async Task AddAsync(T entity) => await _dbSet.AddAsync(entity);
    public void Update(T entity) => _dbSet.Update(entity);
    public void Delete(T entity) => _dbSet.Remove(entity);
}

// Specific — ENTITY'GA XOS so'rovlar (Generic bunga YETARLI EMAS)
public interface IEmployeeRepository : IRepository<Employee>
{
    Task<List<Employee>> GetByDepartmentAsync(int departmentId);
    Task<Employee?> GetWithDetailsAsync(int id); // Include bilan
}
```

### 3.2 Unit of Work

```csharp
public interface IUnitOfWork : IDisposable
{
    IEmployeeRepository Employees { get; }
    IRepository<Department> Departments { get; }
    Task<int> SaveChangesAsync();
    Task BeginTransactionAsync();
    Task CommitAsync();
    Task RollbackAsync();
}

public class UnitOfWork : IUnitOfWork
{
    private readonly AppDbContext _context;
    private IDbContextTransaction? _transaction;

    public IEmployeeRepository Employees { get; }
    public IRepository<Department> Departments { get; }

    public UnitOfWork(AppDbContext context, IEmployeeRepository employees)
    {
        _context = context;
        Employees = employees;
        Departments = new Repository<Department>(context);
    }

    public async Task<int> SaveChangesAsync() => await _context.SaveChangesAsync();

    public async Task BeginTransactionAsync() => _transaction = await _context.Database.BeginTransactionAsync();
    public async Task CommitAsync() { await _transaction!.CommitAsync(); }
    public async Task RollbackAsync() { await _transaction!.RollbackAsync(); }

    public void Dispose() => _context.Dispose();
}
```

```csharp
// Bir nechta Repository — BITTA transaction ichida
await _unitOfWork.BeginTransactionAsync();
try
{
    await _unitOfWork.Employees.AddAsync(newEmployee);
    _unitOfWork.Departments.Update(department); // department.EmployeeCount++
    await _unitOfWork.SaveChangesAsync();
    await _unitOfWork.CommitAsync();
}
catch
{
    await _unitOfWork.RollbackAsync();
    throw;
}
```

### 3.3 DbContext o'zi Repository + Unit of Work

```
MUHIM TUSHUNCHA: EF Core'ning DbContext'i O'ZI ALLAQACHON:
  - Repository (DbSet<T> orqali — Add, Remove, Find, Query)
  - Unit of Work (SaveChanges() — BARCHA o'zgarishlarni BITTA
    transaction sifatida saqlaydi)

QO'SHIMCHA Repository/UoW qatlami — bu holda KO'PINCHA "ortiqcha
abstraksiya" (leaky abstraction) hisoblanadi — chunki DbContext
ALLAQACHON shu vazifani bajaradi.
```

### 3.4 CQRS + MediatR'da Repository nima uchun shart emas

```csharp
// MediatR Handler — TO'G'RIDAN DbContext bilan ishlaydi
public class GetEmployeeHandler : IRequestHandler<GetEmployeeQuery, EmployeeDto>
{
    private readonly AppDbContext _context; // Repository EMAS, TO'G'RIDAN DbContext!

    public async Task<EmployeeDto> Handle(GetEmployeeQuery request, CancellationToken ct)
    {
        var emp = await _context.Employees.AsNoTracking()
            .FirstOrDefaultAsync(e => e.Id == request.Id, ct);
        return _mapper.Map<EmployeeDto>(emp);
    }
}
```

```
Sabab: Har bir Handler — ALLAQACHON "bitta operatsiya" (Single
Responsibility) ni ifodalaydi. Handler'ning O'ZI — Repository
metodi kabi "aniq bir vazifa" bajaradi. Repository qatlami
QO'SHILSA — BIR XIL narsani IKKI MARTA abstraksiya qilish bo'ladi
(Handler ustida Repository, Repository ustida DbContext).

CQRS + MediatR + EF Core — Repository'ni ALMASHTIRADI (har Handler
= "o'z repository metodi").
```

### 3.5 ADO.NET loyihasida Repository nima uchun SHART

```
ADO.NET'da — DbContext YO'Q, faqat NpgsqlConnection/NpgsqlCommand
BOR — bu holatda:
  - SQL kodi HAR JOYGA (Controller ichiga) TARQALIB KETISHI MUMKIN
  - Bir xil SQL TAKRORLANISHI mumkin
  - Repository — SQL'ni BITTA joyga TO'PLAYDI, Controller faqat
    HTTP bilan shug'ullanadi

Junior-D/05-ado-net hujjatida ko'rsatilganidek — ADO.NET loyihasida
Repository Pattern DEYARLI MAJBURIY.
```

### 3.6 Test qilishda afzalligi

```csharp
[Fact]
public async Task GetEmployee_ReturnsCorrectData()
{
    var mockRepo = Substitute.For<IEmployeeRepository>();
    mockRepo.GetByIdAsync(1).Returns(new Employee { Id = 1, FullName = "Orzibek" });

    var service = new EmployeeService(mockRepo);
    var result = await service.GetByIdAsync(1);

    Assert.Equal("Orzibek", result.FullName);
}
```

Repository interfeysi — **haqiqiy DB'siz**, mock orqali test qilish
imkonini beradi (garchi zamonaviy yondashuvda `DbContext`ning o'zini
ham ba'zi holatlarda in-memory provider bilan test qilish mumkin).

## 4. Kod — Repository + Unit of Work birga ishlatish

```csharp
public class OrderService
{
    private readonly IUnitOfWork _unitOfWork;

    public async Task CreateOrderAsync(CreateOrderDto dto)
    {
        var order = new Order { CustomerId = dto.CustomerId };
        await _unitOfWork.Orders.AddAsync(order);

        var customer = await _unitOfWork.Customers.GetByIdAsync(dto.CustomerId);
        customer.OrderCount++;
        _unitOfWork.Customers.Update(customer);

        await _unitOfWork.SaveChangesAsync(); // IKKALASI HAM BITTA transaction'da saqlanadi
    }
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| ADO.NET (DbContext yo'q) loyiha | Repository + UnitOfWork MAJBURIY |
| EF Core + CQRS/MediatR | Repository ODATDA SHART EMAS — DbContext to'g'ridan |
| Ko'p turli DB provayder qo'llab-quvvatlash kerak | Repository (abstraksiya foydali) |
| Oddiy CRUD API, EF Core | DbContext to'g'ridan, ortiqcha qatlam qo'shmang |

## 6. Muhim nuqtalar

- EF Core loyihalarda Repository/UnitOfWork qo'shish — ko'pincha
  **"ortiqcha muhandislik"** (over-engineering) hisoblanadi, chunki
  DbContext ALLAQACHON shu ikki patternni implement qiladi.
- CQRS/MediatR arxitekturasi — Repository'ning **zamonaviy
  o'rinbosari** hisoblanadi (har Handler — o'zining "so'rovi").
- Repository — faqat **haqiqiy abstraksiya kerak bo'lganda**
  (masalan bir necha DB turi, yoki ADO.NET) qo'shilishi kerak.

## 7. Imtihon savollari

1. Repository Pattern qaysi muammoni hal qiladi?
2. Unit of Work nima va u nima uchun Repository bilan birga
   ishlatiladi?
3. EF Core'ning DbContext'i o'zi qanday qilib Repository va Unit of
   Work vazifasini bajaradi?
4. CQRS + MediatR arxitekturasida Repository nima uchun ko'pincha
   SHART EMAS?
5. ADO.NET loyihasida Repository nima uchun DEYARLI MAJBURIY?
6. Generic Repository va Specific Repository orasidagi farq nima?
