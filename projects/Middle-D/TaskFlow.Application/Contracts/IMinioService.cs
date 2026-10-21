namespace TaskFlow.Application.Contracts;

public interface IMinioService
{
    Task<string> UploadFileAsync(Stream fileStream, string fileName, string contentType);
    Task<string> GetFileUrlAsync(string objectName);
    Task DeleteFileAsync(string objectName);
}