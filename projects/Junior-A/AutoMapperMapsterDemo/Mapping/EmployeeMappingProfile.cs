using AutoMapper;
using AutoMapperMapsterDemo.Dtos;
using AutoMapperMapsterDemo.Models;

namespace AutoMapperMapsterDemo.Mapping;

public class EmployeeMappingProfile : Profile
{
    public EmployeeMappingProfile()
    {
        // ===== 1. ASOSIY mapping + ForMember (custom property) =====
        CreateMap<Employee, EmployeeDto>()
            .ForMember(dest => dest.DepartmentName,
                opt => opt.MapFrom(src => src.Department != null ? src.Department.Name : "Bo'limsiz"))

            // ===== 2. CONDITIONAL MAPPING =====
            // Bonus FAQAT BaseSalary > 5,000,000 bo'lgan xodimlarga MAPPING qilinadi.
            // Condition() — shart tekshiradi; agar FALSE bo'lsa, MapFrom UMUMAN
            // ishlamaydi va Bonus o'zining DEFAULT qiymatida (null) qoladi.
            .ForMember(dest => dest.Bonus, opt =>
            {
                opt.Condition(src => src.BaseSalary > 5_000_000);
                opt.MapFrom(src => src.BaseSalary * 0.1m);
            })

            // ===== 3. MAPPING INHERITANCE — bazaviy Profile'ga sub-klasslarni "ulash" =====
            .Include<Manager, ManagerDto>()
            .Include<Contractor, ContractorDto>();

        // Sub-klass mapping'lari — IncludeBase() orqali bazaviy mappingni
        // "meros oladi" (FullName, DepartmentName, Bonus — qayta yozilmaydi,
        // yuqoridagi Employee->EmployeeDto konfiguratsiyasidan avtomatik ko'chadi!)
        CreateMap<Manager, ManagerDto>()
            .IncludeBase<Employee, EmployeeDto>();

        CreateMap<Contractor, ContractorDto>()
            .IncludeBase<Employee, EmployeeDto>();
    }
}
